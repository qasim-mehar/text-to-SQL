import sqlite3
from datetime import datetime, timedelta
import random

conn = sqlite3.connect("company.db")
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

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
cursor.execute("CREATE INDEX idx_emp_dept ON employees(department_id);")
cursor.execute("CREATE INDEX idx_sales_date ON sales(sale_date);")
cursor.execute("CREATE INDEX idx_expense_date ON expenses(expense_date);")

conn.commit()
