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


# 3. PROMPT — includes strict anti-pattern rules


def build_prompt() -> ChatPromptTemplate:
    example_prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{question}"),
            ("ai", "{sql}"),
        ]
    )
    few_shot = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=FEW_SHOT_EXAMPLES,
    )

    system = """You are an expert SQLite query generator. Your output must be a single, correct, executable SQLite query.

━━━ STRICT OUTPUT RULES ━━━
1. Output ONLY the raw SQL — no markdown, no backticks, no explanation, no comments.
2. Never use SELECT * — always name specific columns.
3. Use table aliases (e for employees, d for departments, s for sales, ex for expenses).
4. Always end with a semicolon.
5. If the question is completely unrelated to the schema, output exactly: NULL

━━━ ACCURACY RULES (CRITICAL) ━━━

RULE A — PRE-AGGREGATION (most common bug):
When joining two tables that BOTH have multiple rows per entity (e.g. sales + expenses,
or orders + order_items), NEVER join them raw and then GROUP BY.
This causes row multiplication and wrong SUM values.
ALWAYS pre-aggregate each table in a subquery or CTE first, then join the results.

  WRONG:
    SELECT e.id, SUM(s.amount), SUM(ex.amount)
    FROM employees e
    JOIN sales s ON e.id = s.rep_id
    JOIN expenses ex ON e.dept_id = ex.dept_id   ← fan-out here
    GROUP BY e.id

  CORRECT:
    WITH rep_sales AS (SELECT rep_id, SUM(amount) AS total FROM sales GROUP BY rep_id),
         dept_exp  AS (SELECT dept_id, SUM(amount) AS total FROM expenses GROUP BY dept_id)
    SELECT e.id, rep_sales.total, dept_exp.total
    FROM employees e
    JOIN rep_sales ON e.id = rep_sales.rep_id
    LEFT JOIN dept_exp ON e.dept_id = dept_exp.dept_id

RULE B — WINDOW FUNCTIONS vs SELF-JOINS:
When computing per-group statistics (avg salary per department), use window functions.
NEVER combine a window function with a self-join on the same table.
Use a CTE to compute the window function first, then filter in the outer query.

  WRONG:
    SELECT e.salary, AVG(e2.salary) OVER (PARTITION BY e.dept_id)
    FROM employees e JOIN employees e2 ON e.dept_id = e2.dept_id  ← multiplies rows

  CORRECT:
    WITH stats AS (
        SELECT *, AVG(salary) OVER (PARTITION BY dept_id) AS dept_avg FROM employees
    )
    SELECT * FROM stats WHERE salary > dept_avg

RULE C — DIVISION SAFETY:
Always wrap denominators in NULLIF(value, 0) to prevent division-by-zero errors.
  CORRECT: value / NULLIF(denominator, 0)

RULE D — NULL HANDLING:
Use COALESCE(value, 0) when a LEFT JOIN column might be NULL due to no matching rows.

RULE E — DATE FILTERING IN SQLITE:
Use strftime('%Y', date_column) = '2024' for year filtering.
Use strftime('%Y-%m', date_column) for month grouping.

RULE F — SELF-JOINS FOR HIERARCHY:
For management chains, use LEFT JOIN employees m ON e.manager_id = m.employee_id.
Repeat for each level. This is correct — do not avoid it.

RULE G — ROLE FILTERING:
When the user says "sales reps", "managers", "engineers" or any job role,
always add a WHERE filter on job_title using LIKE '%keyword%'.
Do NOT return all employees who happen to have data in a fact table.
The fact table (sales, expenses) having a row for an employee does NOT
mean that employee has that role — always filter by job_title or department.

━━━ SCHEMA ━━━
{schema}

{error_context}"""

    return ChatPromptTemplate.from_messages(
        [
            ("system", system),
            few_shot,
            ("human", "{question}"),
        ]
    )


# 4. CLEAN SQL OUTPUT


def clean_sql(raw: str) -> str:
    sql = raw.strip()
    sql = re.sub(r"^```(?:sql)?\s*\n?", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\n?```$", "", sql)
    sql = sql.strip()
    if sql.upper() == "NULL":
        return "NULL"
    if ";" in sql:
        sql = sql[: sql.index(";") + 1]
    return sql.strip()


# 5. VALIDATION — blocks all destructive SQL


def validate_sql(sql: str) -> str:
    if sql.upper() == "NULL":
        return sql
    tokens = sql.upper().split()
    if not tokens:
        raise ValueError("Empty SQL generated.")
    if tokens[0] != "SELECT" and tokens[0] != "WITH":
        raise ValueError(f"Only SELECT/WITH queries allowed. Got: '{tokens[0]}'")
    found = FORBIDDEN.intersection(set(tokens))
    if found:
        raise ValueError(f"Forbidden keyword(s) in query: {found}")
    return sql


# 6. EXECUTION — uses shared engine, caps rows


def execute_sql(sql: str) -> dict:
    if sql.upper() == "NULL":
        return {
            "sql": sql,
            "data": None,
            "error": "Question is unrelated to the database schema.",
        }
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            rows = result.fetchmany(MAX_ROWS)
            columns = list(result.keys())
            data = [dict(zip(columns, row)) for row in rows]
            return {"sql": sql, "data": data, "error": None}
    except exc.SQLAlchemyError as e:
        return {"sql": sql, "data": None, "error": str(e)}
