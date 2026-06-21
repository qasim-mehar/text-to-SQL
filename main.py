"""
QueryBridge — High-Accuracy Text-to-SQL Pipeline
Key upgrades over basic version:
  - DDL schema format (LLMs understand CREATE TABLE better than JSON)
  - SQL anti-pattern rules in prompt (teaches what NOT to do)
  - Few-shot examples covering joins, window functions, CTEs, self-joins
  - Query complexity classifier (simple vs analytical vs recursive)
  - Self-correcting retry loop
  - Pre-aggregation pattern enforced via prompt
"""

from sqlalchemy import create_engine, inspect, text, exc
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv
import os, re, logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("QueryBridge")

DB_URL = os.getenv("DATABASE_URL", "sqlite:///company.db")
MODEL_NAME = os.getenv("LLM_MODEL", "mistral-medium-3-5")
MAX_ROWS = int(os.getenv("MAX_ROWS", "500"))

#  Single engine + model instance
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
model = ChatMistralAI(model=MODEL_NAME, temperature=0)

FORBIDDEN = {
    "DROP",
    "DELETE",
    "UPDATE",
    "INSERT",
    "ALTER",
    "TRUNCATE",
    "REPLACE",
    "CREATE",
}


# 1. SCHEMA — DDL format, includes types + FK relationships


def get_schema() -> str:
    inspector = inspect(engine)
    ddl_parts = []
    for table in inspector.get_table_names():
        cols = inspector.get_columns(table)
        fks = inspector.get_foreign_keys(table)
        col_defs = [f"  {c['name']} {c['type']}" for c in cols]
        fk_defs = [
            f"  FOREIGN KEY ({', '.join(fk['constrained_columns'])}) "
            f"REFERENCES {fk['referred_table']} ({', '.join(fk['referred_columns'])})"
            for fk in fks
        ]
        body = ",\n".join(col_defs + fk_defs)
        ddl_parts.append(f"CREATE TABLE {table} (\n{body}\n);")
    return "\n\n".join(ddl_parts)


SCHEMA = get_schema()
logger.info(f"Schema loaded: {SCHEMA.count('CREATE TABLE')} tables.")


# FEW-SHOT EXAMPLES

FEW_SHOT_EXAMPLES = [
    #  Simple aggregation + JOIN ─
    {
        "question": "How many employees are in each department?",
        "sql": """SELECT d.department_name, COUNT(e.employee_id) AS employee_count
FROM departments d
LEFT JOIN employees e ON d.department_id = e.department_id
GROUP BY d.department_name
ORDER BY employee_count DESC;""",
    },
    # PRE-AGGREGATION before joining two fact tables
    {
        "question": "Which sales reps generated more revenue than their department's total expenses in 2024?",
        "sql": """SELECT
    e.employee_id,
    e.first_name,
    e.last_name,
    e.job_title,
    rep_sales.total_sales,
    COALESCE(dept_exp.total_expenses, 0) AS total_department_expenses
FROM employees e
JOIN (
    SELECT sales_rep_id, SUM(amount_usd) AS total_sales
    FROM sales
    WHERE strftime('%Y', sale_date) = '2024'
    GROUP BY sales_rep_id
) rep_sales ON e.employee_id = rep_sales.sales_rep_id
LEFT JOIN (
    SELECT department_id, SUM(amount_usd) AS total_expenses
    FROM expenses
    WHERE strftime('%Y', expense_date) = '2024'
    GROUP BY department_id
) dept_exp ON e.department_id = dept_exp.department_id
WHERE rep_sales.total_sales > COALESCE(dept_exp.total_expenses, 0)
ORDER BY rep_sales.total_sales DESC;""",
    },
    # Window functions  NO self-join needed
    {
        "question": "List employees earning above their department average, with the difference.",
        "sql": """WITH dept_stats AS (
    SELECT
        employee_id,
        first_name,
        last_name,
        salary,
        department_id,
        ROUND(AVG(salary) OVER (PARTITION BY department_id), 2) AS dept_avg_salary
    FROM employees
)
SELECT
    ds.employee_id,
    ds.first_name,
    ds.last_name,
    ds.salary,
    d.department_name,
    ds.dept_avg_salary,
    ROUND(ds.salary - ds.dept_avg_salary, 2) AS salary_difference
FROM dept_stats ds
JOIN departments d ON ds.department_id = d.department_id
WHERE ds.salary > ds.dept_avg_salary
ORDER BY salary_difference DESC;""",
    },
    # Self-join for hierarchy (management chain)
    {
        "question": "Show each employee's 2-level management chain.",
        "sql": """SELECT
    e.employee_id,
    e.first_name  || ' ' || e.last_name  AS employee,
    m1.first_name || ' ' || m1.last_name AS direct_manager,
    m2.first_name || ' ' || m2.last_name AS skip_level_manager
FROM employees e
LEFT JOIN employees m1 ON e.manager_id  = m1.employee_id
LEFT JOIN employees m2 ON m1.manager_id = m2.employee_id
ORDER BY skip_level_manager NULLS LAST, direct_manager NULLS LAST, employee;""",
    },
    #  CTE for multi-step analytical queries
    {
        "question": "Which department has the highest ratio of total sales to total expenses in 2024?",
        "sql": """WITH dept_sales AS (
    SELECT e.department_id, SUM(s.amount_usd) AS total_sales
    FROM sales s
    JOIN employees e ON s.sales_rep_id = e.employee_id
    WHERE strftime('%Y', s.sale_date) = '2024'
    GROUP BY e.department_id
),
dept_expenses AS (
    SELECT department_id, SUM(amount_usd) AS total_expenses
    FROM expenses
    WHERE strftime('%Y', expense_date) = '2024'
    GROUP BY department_id
)
SELECT
    d.department_name,
    ds.total_sales,
    COALESCE(de.total_expenses, 0) AS total_expenses,
    ROUND(ds.total_sales / NULLIF(COALESCE(de.total_expenses, 0), 0), 2) AS sales_to_expense_ratio
FROM dept_sales ds
JOIN departments d ON ds.department_id = d.department_id
LEFT JOIN dept_expenses de ON ds.department_id = de.department_id
ORDER BY sales_to_expense_ratio DESC
LIMIT 1;""",
    },
    #  NULLIF to prevent division by zero
    {
        "question": "What is each project's budget utilization percentage based on hours?",
        "sql": """SELECT
    p.project_name,
    p.budget_usd,
    p.status,
    COALESCE(ph.total_spent, 0) AS total_spent,
    ROUND(COALESCE(ph.total_spent, 0) * 100.0 / NULLIF(p.budget_usd, 0), 1) AS utilization_pct
FROM projects p
LEFT JOIN (
    SELECT project_id, SUM(amount_usd) AS total_spent
    FROM expenses
    GROUP BY project_id
) ph ON p.project_id = ph.project_id
ORDER BY utilization_pct DESC NULLS LAST;""",
    },
    # Ranking with window functions
    {
        "question": "Rank employees by salary within each department.",
        "sql": """SELECT
    e.first_name,
    e.last_name,
    d.department_name,
    e.salary,
    RANK() OVER (PARTITION BY e.department_id ORDER BY e.salary DESC) AS salary_rank
FROM employees e
JOIN departments d ON e.department_id = d.department_id
ORDER BY d.department_name, salary_rank;""",
    },
    # Date filtering + aggregation
    {
        "question": "Show monthly sales totals for 2024.",
        "sql": """SELECT
    strftime('%Y-%m', sale_date) AS month,
    COUNT(sale_id)               AS num_sales,
    ROUND(SUM(amount_usd), 2)    AS total_revenue
FROM sales
WHERE strftime('%Y', sale_date) = '2024'
GROUP BY strftime('%Y-%m', sale_date)
ORDER BY month;""",
    },
]
