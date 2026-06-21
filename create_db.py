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

    # 1. DEPARTMENTS
    # 6 departments. Finance has NO expenses → tests LEFT JOIN + NULL queries.

    depts = [
        #  name             location         budget_usd
        ("Engineering", "San Francisco", 5_000_000),  # 1
        ("Sales", "New York", 3_000_000),  # 2
        ("Marketing", "Chicago", 1_500_000),  # 3
        ("Product", "San Francisco", 1_200_000),  # 4
        ("HR", "Austin", 800_000),  # 5
        ("Finance", "New York", 900_000),  # 6 ← zero expenses (intentional)
    ]
    cursor.executemany(
        "INSERT INTO departments (department_name, location, budget_usd) VALUES (?,?,?);",
        depts,
    )

    # 2. EMPLOYEES  (25 people, 3-level hierarchy)
    #
    # Hierarchy:
    #   Level 1 (no manager):   Alice(1), Diana(4), George(7), Ian(9), Kevin(11), Rachel(21)
    #   Level 2 (mgr=L1):       Bob(2),Charlie(3),Mike(13),Oscar(15) → mgr=Alice(1)
    #                            Evan(5),Fiona(6),Laura(12),Tom(22)  → mgr=Diana(4)
    #                            Hannah(8),Nina(14),Sara(23)          → mgr=George(7)
    #                            Julia(10),Liam(24)                   → mgr=Ian(9)
    #                            Finance team                         → mgr=Rachel(21)
    #   Level 3 (mgr=L2):       Priya(16),James(17)                  → mgr=Oscar(15)
    #                            Chen(18),Amara(19)                   → mgr=Bob(2)
    #
    # Special cases:
    #   Kevin(11) — no manager, no direct reports (orphan test, query 17)
    #   Salaries vary enough to make per-dept ranking & percentile interesting
    #   Some employees hired before 2022 (tenure > 2yr, below avg salary test)

    employees = [
        # id  first       last          email                          hire_date      dept  title                      salary    mgr
        (
            1,
            "Alice",
            "Smith",
            "alice.smith@co.com",
            "2020-03-15",
            1,
            "Engineering Manager",
            145_000,
            None,
        ),
        (
            2,
            "Bob",
            "Jones",
            "bob.jones@co.com",
            "2021-06-01",
            1,
            "Senior Engineer",
            120_000,
            1,
        ),
        (
            3,
            "Charlie",
            "Brown",
            "charlie.brown@co.com",
            "2022-01-10",
            1,
            "Software Engineer",
            95_000,
            1,
        ),
        (
            4,
            "Diana",
            "Prince",
            "diana.prince@co.com",
            "2019-11-20",
            2,
            "VP of Sales",
            160_000,
            None,
        ),
        (
            5,
            "Evan",
            "Wright",
            "evan.wright@co.com",
            "2020-08-05",
            2,
            "Sales Rep",
            85_000,
            4,
        ),
        (
            6,
            "Fiona",
            "Garcia",
            "fiona.garcia@co.com",
            "2021-02-14",
            2,
            "Account Executive",
            90_000,
            4,
        ),
        (
            7,
            "George",
            "Miller",
            "george.miller@co.com",
            "2023-03-01",
            3,
            "Marketing Lead",
            88_000,
            None,
        ),
        (
            8,
            "Hannah",
            "Davis",
            "hannah.davis@co.com",
            "2022-07-20",
            3,
            "Content Specialist",
            65_000,
            7,
        ),
        (
            9,
            "Ian",
            "Wilson",
            "ian.wilson@co.com",
            "2020-05-12",
            4,
            "Product Manager",
            115_000,
            None,
        ),
        (
            10,
            "Julia",
            "Moore",
            "julia.moore@co.com",
            "2021-09-01",
            4,
            "Product Designer",
            98_000,
            9,
        ),
        (
            11,
            "Kevin",
            "Taylor",
            "kevin.taylor@co.com",
            "2023-01-15",
            5,
            "HR Generalist",
            60_000,
            None,
        ),  # orphan
        (
            12,
            "Laura",
            "Anderson",
            "laura.anderson@co.com",
            "2018-04-10",
            2,
            "Sales Rep",
            92_000,
            4,
        ),
        (
            13,
            "Mike",
            "Thomas",
            "mike.thomas@co.com",
            "2022-11-01",
            1,
            "Software Engineer",
            92_000,
            1,
        ),
        (
            14,
            "Nina",
            "Jackson",
            "nina.jackson@co.com",
            "2023-06-15",
            3,
            "SEO Analyst",
            58_000,
            7,
        ),
        (
            15,
            "Oscar",
            "White",
            "oscar.white@co.com",
            "2019-08-20",
            1,
            "Staff Engineer",
            135_000,
            1,
        ),
        (
            16,
            "Priya",
            "Sharma",
            "priya.sharma@co.com",
            "2023-03-10",
            1,
            "Junior Engineer",
            78_000,
            15,
        ),  # L3
        (
            17,
            "James",
            "Lee",
            "james.lee@co.com",
            "2023-07-01",
            1,
            "Junior Engineer",
            76_000,
            15,
        ),  # L3
        (
            18,
            "Chen",
            "Wei",
            "chen.wei@co.com",
            "2022-09-12",
            1,
            "Software Engineer",
            96_000,
            2,
        ),  # L3
        (
            19,
            "Amara",
            "Diallo",
            "amara.diallo@co.com",
            "2023-01-20",
            1,
            "Software Engineer",
            93_000,
            2,
        ),  # L3
        (
            20,
            "Sara",
            "Lopez",
            "sara.lopez@co.com",
            "2022-05-10",
            3,
            "Marketing Analyst",
            72_000,
            7,
        ),
        (
            21,
            "Rachel",
            "Kim",
            "rachel.kim@co.com",
            "2018-11-01",
            6,
            "Finance Director",
            155_000,
            None,
        ),
        (
            22,
            "Tom",
            "Harris",
            "tom.harris@co.com",
            "2020-03-22",
            2,
            "Sales Rep",
            87_000,
            4,
        ),
        (
            23,
            "Yuki",
            "Tanaka",
            "yuki.tanaka@co.com",
            "2021-08-15",
            3,
            "Brand Strategist",
            80_000,
            7,
        ),
        (
            24,
            "Liam",
            "O'Brien",
            "liam.obrien@co.com",
            "2022-04-01",
            4,
            "UX Researcher",
            88_000,
            9,
        ),
        (
            25,
            "Fatima",
            "Malik",
            "fatima.malik@co.com",
            "2019-06-17",
            6,
            "Financial Analyst",
            95_000,
            21,
        ),
    ]

    cursor.executemany(
        """
        INSERT INTO employees
            (employee_id, first_name, last_name, email, hire_date, department_id, job_title, salary, manager_id)
        VALUES (?,?,?,?,?,?,?,?,?);
    """,
        employees,
    )

    # 3. PROJECTS

    projects = [
        ("Website Redesign", 3, "Completed", 120_000, "2023-01-15", "2023-06-30"),
        ("Mobile App v2", 1, "Active", 300_000, "2023-09-01", "2024-12-31"),
        ("CRM Integration", 2, "Active", 150_000, "2024-01-10", "2024-08-15"),
        ("Q4 Ad Campaign", 3, "Active", 80_000, "2024-10-01", "2024-12-31"),
        ("Data Pipeline", 1, "Completed", 200_000, "2023-03-01", "2024-01-15"),
        ("Finance Dashboard", 6, "Active", 90_000, "2024-03-01", "2024-09-30"),
        ("HR Platform", 5, "Cancelled", 45_000, "2024-01-01", "2024-04-01"),
    ]
    cursor.executemany(
        "INSERT INTO projects (project_name, department_id, status, budget_usd, start_date, end_date) VALUES (?,?,?,?,?,?);",
        projects,
    )

    # 4. SALES
    customers = [
        "Acme Corp",
        "Globex",
        "Initech",
        "Umbrella",
        "Stark Industries",
        "Wayne Enterprises",
        "Cyberdyne Systems",
        "Oscorp",
        "Weyland Corp",
        "Massive Dynamic",
    ]

    products_amounts = {
        "SaaS Enterprise": (30_000, 95_000),
        "Consulting": (25_000, 80_000),
        "SaaS Pro": (10_000, 45_000),
        "SaaS Basic": (5_000, 18_000),
        "Support": (3_000, 12_000),
    }

    regions = ["North America", "Europe", "Asia"]

    # Sales reps and their monthly quota targets (shapes their output)
    rep_profiles = {
        5: {
            "name": "Evan",
            "monthly_sales": 2,
            "preferred_products": ["SaaS Pro", "SaaS Basic"],
            "std": "low",
        },
        6: {
            "name": "Fiona",
            "monthly_sales": 2,
            "preferred_products": ["SaaS Enterprise", "Consulting"],
            "std": "high",
        },
        12: {
            "name": "Laura",
            "monthly_sales": 3,
            "preferred_products": ["SaaS Enterprise", "SaaS Pro"],
            "std": "medium",
        },
        22: {
            "name": "Tom",
            "monthly_sales": 2,
            "preferred_products": ["SaaS Pro", "SaaS Basic"],
            "std": "medium",
        },
        4: {
            "name": "Diana",
            "monthly_sales": 1,
            "preferred_products": ["Consulting", "SaaS Enterprise"],
            "std": "high",
        },
    }

    sales_rows = []

    for month in range(1, 13):  # all 12 months of 2024
        for rep_id, profile in rep_profiles.items():
            n_sales = profile["monthly_sales"]

            # Evan (std=low) gets consistent amounts — lowest stddev
            # Fiona/Diana (std=high) get wide swings

            for _ in range(n_sales):
                product = random.choice(profile["preferred_products"])
                lo, hi = products_amounts[product]

                if profile["std"] == "low":
                    # Narrow band: ±10% of midpoint
                    mid = (lo + hi) / 2
                    amt = round(random.uniform(mid * 0.90, mid * 1.10), 2)
                elif profile["std"] == "high":
                    amt = round(random.uniform(lo, hi), 2)
                else:
                    amt = round(random.uniform(lo * 1.1, hi * 0.9), 2)

                # Each rep must cover ALL regions across the year
                # First 3 months: rotate through all 3 regions deterministically
                if month <= 3:
                    region = regions[(month - 1) % 3]
                else:
                    region = random.choice(regions)

                day = random.randint(1, 28)
                date = f"2024-{month:02d}-{day:02d}"

                sales_rows.append(
                    (
                        random.choice(customers),
                        date,
                        amt,
                        product,
                        rep_id,
                        region,
                    )
                )

    # Extra big deals from Laura to make her clearly #1
    for month in [3, 6, 9, 11]:
        sales_rows.append(
            (
                "Acme Corp",
                f"2024-{month:02d}-15",
                round(random.uniform(70_000, 95_000), 2),
                "SaaS Enterprise",
                12,
                random.choice(regions),
            )
        )

    cursor.executemany(
        "INSERT INTO sales (customer_name, sale_date, amount_usd, product, sales_rep_id, region) VALUES (?,?,?,?,?,?);",
        sales_rows,
    )

    # 5. EXPENSES — 200 rows
    #
    # Design goals:
    #   - Dept 6 (Finance) gets ZERO expenses → tests "dept with no expenses" query (Q16)
    #   - Dept 2 (Sales) gets high expenses → some months expenses > sales (interesting HAVING)
    #   - Realistic category amounts:
    #       Travel:          $800–$5,000
    #       Software:        $200–$3,000
    #       Hardware:        $500–$8,000
    #       Training:        $1,000–$6,000
    #       Events:          $2,000–$12,000
    #       Office Supplies: $50–$800
    #   - Spread across all 12 months of 2024

    category_ranges = {
        "Travel": (800, 5_000),
        "Software": (200, 3_000),
        "Hardware": (500, 8_000),
        "Training": (1_000, 6_000),
        "Events": (2_000, 12_000),
        "Office Supplies": (50, 800),
    }

    # dept_id → how many expense rows per month (Finance=6 gets 0)
    dept_expense_volume = {1: 4, 2: 5, 3: 3, 4: 2, 5: 2, 6: 0}

    expenses_rows = []
    for month in range(1, 13):
        for dept_id, volume in dept_expense_volume.items():
            for _ in range(volume):
                category = random.choice(list(category_ranges.keys()))
                lo, hi = category_ranges[category]
                amt = round(random.uniform(lo, hi), 2)
                day = random.randint(1, 28)
                date = f"2024-{month:02d}-{day:02d}"
                expenses_rows.append(
                    (
                        dept_id,
                        category,
                        amt,
                        date,
                        f"{category} - Q{((month - 1) // 3) + 1}",
                    )
                )

    cursor.executemany(
        "INSERT INTO expenses (department_id, category, amount_usd, expense_date, description) VALUES (?,?,?,?,?);",
        expenses_rows,
    )

    conn.commit()


seed()
conn.close()
