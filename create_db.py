import sqlite3
from datetime import datetime, timedelta
import random

conn = sqlite3.connect("company.db")
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

# Drop existing tables (clean slate for re-runs)
cursor.execute("DROP TABLE IF EXISTS expenses;")
cursor.execute("DROP TABLE IF EXISTS sales;")
cursor.execute("DROP TABLE IF EXISTS projects;")
cursor.execute("DROP TABLE IF EXISTS employees;")
cursor.execute("DROP TABLE IF EXISTS departments;")

# Creating tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS departments (
    department_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    department_name TEXT NOT NULL UNIQUE,
    location        TEXT NOT NULL,
    budget_usd      REAL
);
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS employees (
    employee_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name      TEXT NOT NULL,
    last_name       TEXT NOT NULL,
    email           TEXT NOT NULL UNIQUE,
    hire_date       DATE NOT NULL,
    department_id   INTEGER NOT NULL,
    job_title       TEXT NOT NULL,
    salary          REAL NOT NULL,
    manager_id      INTEGER,
    FOREIGN KEY (department_id) REFERENCES departments(department_id),
    FOREIGN KEY (manager_id) REFERENCES employees(employee_id)
);
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS projects (
    project_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name    TEXT NOT NULL,
    department_id   INTEGER NOT NULL,
    status          TEXT CHECK (status IN ('Active', 'Completed', 'Cancelled')),
    budget_usd      REAL,
    start_date      DATE,
    end_date        DATE,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    sale_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name   TEXT NOT NULL,
    sale_date       DATE NOT NULL,
    amount_usd      REAL NOT NULL,
    product         TEXT,
    sales_rep_id    INTEGER NOT NULL,
    region          TEXT,
    FOREIGN KEY (sales_rep_id) REFERENCES employees(employee_id)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    expense_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    department_id   INTEGER NOT NULL,
    category        TEXT NOT NULL,
    amount_usd      REAL NOT NULL,
    expense_date    DATE NOT NULL,
    description     TEXT,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);
""")

# INDEXNG TABLES
cursor.execute("CREATE INDEX IF NOT EXISTS idx_emp_dept ON employees(department_id);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_expense_date ON expenses(expense_date);")

conn.commit()


# SEED DATA
def seed():

    depts = [
        ("Engineering", "San Francisco", 5000000),
        ("Sales", "New York", 3000000),
        ("Marketing", "Chicago", 1500000),
        ("Product", "San Francisco", 1200000),
        ("HR", "Austin", 800000),
    ]
    cursor.executemany(
        "INSERT INTO departments (department_name, location, budget_usd) VALUES (?, ?, ?);",
        depts,
    )

    employees = [
        (
            "Alice",
            "Smith",
            "alice.smith@co.com",
            "2020-03-15",
            1,
            "Engineering Manager",
            145000,
            None,
        ),
        (
            "Bob",
            "Jones",
            "bob.jones@co.com",
            "2021-06-01",
            1,
            "Senior Engineer",
            120000,
            1,
        ),
        (
            "Charlie",
            "Brown",
            "charlie.brown@co.com",
            "2022-01-10",
            1,
            "Software Engineer",
            95000,
            1,
        ),
        (
            "Diana",
            "Prince",
            "diana.prince@co.com",
            "2019-11-20",
            2,
            "VP of Sales",
            160000,
            None,
        ),
        (
            "Evan",
            "Wright",
            "evan.wright@co.com",
            "2020-08-05",
            2,
            "Sales Rep",
            85000,
            4,
        ),
        (
            "Fiona",
            "Garcia",
            "fiona.garcia@co.com",
            "2021-02-14",
            2,
            "Account Executive",
            90000,
            4,
        ),
        (
            "George",
            "Miller",
            "george.miller@co.com",
            "2023-03-01",
            3,
            "Marketing Lead",
            88000,
            None,
        ),
        (
            "Hannah",
            "Davis",
            "hannah.davis@co.com",
            "2022-07-20",
            3,
            "Content Specialist",
            65000,
            7,
        ),
        (
            "Ian",
            "Wilson",
            "ian.wilson@co.com",
            "2020-05-12",
            4,
            "Product Manager",
            115000,
            None,
        ),
        (
            "Julia",
            "Moore",
            "julia.moore@co.com",
            "2021-09-01",
            4,
            "Product Designer",
            98000,
            9,
        ),
        (
            "Kevin",
            "Taylor",
            "kevin.taylor@co.com",
            "2023-01-15",
            5,
            "HR Generalist",
            60000,
            None,
        ),
        (
            "Laura",
            "Anderson",
            "laura.anderson@co.com",
            "2018-04-10",
            2,
            "Sales Rep",
            92000,
            4,
        ),
        (
            "Mike",
            "Thomas",
            "mike.thomas@co.com",
            "2022-11-01",
            1,
            "Software Engineer",
            92000,
            1,
        ),
        (
            "Nina",
            "Jackson",
            "nina.jackson@co.com",
            "2023-06-15",
            3,
            "SEO Analyst",
            58000,
            7,
        ),
        (
            "Oscar",
            "White",
            "oscar.white@co.com",
            "2019-08-20",
            1,
            "Staff Engineer",
            135000,
            1,
        ),
    ]
    cursor.executemany(
        "INSERT INTO employees (first_name, last_name, email, hire_date, department_id, job_title, salary, manager_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?);",
        employees,
    )

    projects = [
        ("Website Redesign", 3, "Completed", 120000, "2023-01-15", "2023-06-30"),
        ("Mobile App v2", 1, "Active", 300000, "2023-09-01", "2024-12-31"),
        ("CRM Integration", 2, "Active", 150000, "2024-01-10", "2024-08-15"),
        ("Q4 Ad Campaign", 3, "Active", 80000, "2024-10-01", "2024-12-31"),
        ("Data Pipeline", 1, "Completed", 200000, "2023-03-01", "2024-01-15"),
    ]
    cursor.executemany(
        "INSERT INTO projects (project_name, department_id, status, budget_usd, start_date, end_date) VALUES (?, ?, ?, ?, ?, ?);",
        projects,
    )

    sales_data = []
    customers = [
        "Acme Corp",
        "Globex",
        "Initech",
        "Umbrella",
        "Stark Ind",
        "Wayne Ent",
        "Cyberdyne",
    ]
    products = ["SaaS Basic", "SaaS Pro", "SaaS Enterprise", "Consulting", "Support"]
    regions = ["North America", "Europe", "Asia"]
    for i in range(40):
        rep = random.choice([4, 5, 6, 12])
        amt = round(random.uniform(5000, 95000), 2)
        d = (datetime(2024, 1, 1) + timedelta(days=random.randint(0, 365))).strftime(
            "%Y-%m-%d"
        )
        sales_data.append(
            (
                random.choice(customers),
                d,
                amt,
                random.choice(products),
                rep,
                random.choice(regions),
            )
        )
    cursor.executemany(
        "INSERT INTO sales (customer_name, sale_date, amount_usd, product, sales_rep_id, region) VALUES (?, ?, ?, ?, ?, ?);",
        sales_data,
    )

    expenses = []
    cats = ["Travel", "Software", "Office Supplies", "Training", "Events", "Hardware"]
    for _ in range(50):
        did = random.randint(1, 5)
        amt = round(random.uniform(50, 8000), 2)
        d = (datetime(2024, 1, 1) + timedelta(days=random.randint(0, 365))).strftime(
            "%Y-%m-%d"
        )
        expenses.append((did, random.choice(cats), amt, d, "Monthly operational cost"))
    cursor.executemany(
        "INSERT INTO expenses (department_id, category, amount_usd, expense_date, description) VALUES (?, ?, ?, ?, ?);",
        expenses,
    )

    conn.commit()


seed()

conn.close()
