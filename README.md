<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Inter&weight=700&size=42&pause=1000&color=F5F5F5&center=true&vCenter=true&width=600&lines=QueryBridge" alt="QueryBridge" />

**Ask your database anything. In plain English.**

<p>
  <img src="https://img.shields.io/badge/Python-3.11+-black?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/LangChain-1C3C3C?style=flat-square&logo=langchain&logoColor=white" />
  <img src="https://img.shields.io/badge/Mistral_AI-FF7000?style=flat-square&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white" />
  <img src="https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black" />
</p>

</div>

---

## Demo



![QueryBridge Demo](./text-to-sql.gif)

## What is this?

QueryBridge is a Text-to-SQL pipeline that converts plain English questions into accurate, executable SQLite queries and runs them instantly against a company analytics database. It is not a wrapper around a single LLM call — it is an engineered pipeline with schema understanding, few-shot teaching, anti-pattern enforcement, and a self-correcting retry loop.

You type: `"Which sales reps generated more revenue than their department's total expenses in 2024?"`

QueryBridge returns the correct SQL and the result table. No SQL knowledge required on your end.

---

## The actual problem this solves

Writing analytics SQL for a relational schema is harder than it looks. You have to know which tables hold what, when to pre-aggregate before joining, how to write window functions without creating row explosions, and a dozen other things that take years to internalize.

The bigger problem is that most text-to-SQL demos fail silently — they produce SQL that runs without errors but returns mathematically wrong numbers. A `JOIN` between two unaggregated fact tables (say, `sales` and `expenses`) inflates every sum by the number of rows in the other table. Nobody tells you this. The query finishes. The results look plausible. The numbers are completely wrong.

This project was built specifically to solve that class of problem, not just the surface-level "generate SQL from a question" task.

---
## What I learned building this

**Prompt engineering is engineering.** Telling an LLM "write SQL" produces mediocre SQL. Teaching it the exact anti-pattern it should avoid, showing it a broken example next to a correct one, and giving it a name for the pattern ("RULE A — PRE-AGGREGATION") produces dramatically better output. The difference is not subtle.

**DDL beats JSON for schema representation.** When you show a language model `CREATE TABLE employees (salary REAL, department_id INTEGER, FOREIGN KEY ...)` it understands the relationships. When you show it `{"employees": ["salary", "department_id"]}` it loses the type information and FK relationships that determine which JOINs are valid.

**Silent failures are worse than loud ones.** A query that crashes returns an error. A query that returns plausible-looking wrong numbers is much more dangerous. The fan-out multiplication bug is particularly nasty because the results look reasonable — they are just inflated by a factor you would never guess without understanding the join mechanics.

**Few-shot examples should target failure modes, not happy paths.** Most SQL tutorials show you `SELECT name FROM employees`. That is not what breaks. What breaks is window functions combined with self-joins, or multi-fact-table aggregation. Every few-shot example in this project covers a specific SQL pattern that the model gets wrong without guidance.

**Temperature 0 is non-negotiable for SQL generation.** SQL is deterministic by nature. The same question should always produce the same query. Any temperature above 0 introduces randomness that can change a `LEFT JOIN` to an `INNER JOIN` or flip an aggregation — small changes that produce silently wrong results.

**The retry loop should never mutate the original question.** Early versions of the retry logic appended the error message to the question string. By retry 3, the model was reading a confused mess of the original question plus two error messages stacked together. The fix is to keep the question immutable and inject error context as a separate prompt variable.

---

## How the pipeline works

```
User question
      │
      ▼
Schema extraction (DDL format — CREATE TABLE statements)
      │
      ▼
Prompt construction
  ├── System prompt with 7 anti-pattern rules
  ├── 8 few-shot examples (one per SQL pattern)
  └── User question
      │
      ▼
Mistral AI  (temperature=0 — deterministic output)
      │
      ▼
Output cleaning  (strip markdown fences, keep first statement only)
      │
      ▼
SQL validation  (SELECT/WITH only — blocks DELETE, DROP, UPDATE, INSERT, ALTER)
      │
      ├── PASS → execute against SQLite → return results
      └── FAIL → inject error into prompt → retry (max 2 times)
```

Every stage has a specific job. Nothing is left to chance.

---

## The SQL accuracy problems we actually solved

<table>
<tr>
<th width="200">Problem</th>
<th>What goes wrong without the fix</th>
<th>How we fixed it</th>
</tr>
<tr>
<td><b>Fan-out multiplication</b></td>
<td>Joining sales (5 rows) with expenses (20 rows) gives 100 rows before GROUP BY. Every SUM is 20× inflated. Query runs. Numbers are garbage.</td>
<td>Rule A in system prompt + a few-shot example showing the pre-aggregation pattern side by side with the broken version</td>
</tr>
<tr>
<td><b>Window function + self-join conflict</b></td>
<td>Combining AVG() OVER (PARTITION BY dept) with a self-join on the same table multiplies rows before the window runs. Results are wrong.</td>
<td>Rule B enforces CTE-first pattern: compute window function in a CTE, filter in the outer query, never self-join for this purpose</td>
</tr>
<tr>
<td><b>Division by zero</b></td>
<td>Any department with zero expenses crashes the query with a runtime error</td>
<td>Rule C mandates NULLIF(denominator, 0) on every division</td>
</tr>
<tr>
<td><b>Role ambiguity</b></td>
<td>"Which sales reps..." returns everyone who has a row in the sales table, including VPs and managers who occasionally close deals</td>
<td>Rule G enforces job_title LIKE '%keyword%' filtering when a role is mentioned</td>
</tr>
<tr>
<td><b>NULL from LEFT JOINs</b></td>
<td>Departments with no expenses return NULL instead of 0, breaking comparisons</td>
<td>Rule D enforces COALESCE(value, 0) on all LEFT JOIN columns used in arithmetic</td>
</tr>
<tr>
<td><b>Destructive queries</b></td>
<td>"Delete all employees" — the LLM might comply</td>
<td>Validator blocks anything that is not SELECT or WITH before it reaches the database</td>
</tr>
</table>

---

## Tech stack

| Layer | Technology | Why |
|---|---|---|
| LLM | Mistral AI `mistral-medium-3-5` | Strong SQL generation, good instruction following, fast |
| LLM framework | LangChain LCEL | Composable pipeline (`prompt \| model \| parser \| cleaner`), clean retry handling |
| Backend | FastAPI + SQLAlchemy | Async, typed, auto-documented API |
| Database | SQLite | Portable, zero infrastructure, perfect for analytics demos |
| Frontend | React 18 + Vite + Tailwind | Fast development, modern tooling |
| Config | pydantic-settings + python-dotenv | Type-safe environment variables |
| Package management | uv | Significantly faster than pip for dependency resolution |

---

## Project structure

```
text-to-SQL/
│
├── backend/
│   ├── app.py                   FastAPI app factory, middleware, router registration
│   ├── config.py                pydantic-settings: DB URL, model name, rate limits
│   │
│   └── features/
│       ├── query/
│       │   ├── router.py        POST /api/query, GET /api/schema, GET /api/history
│       │   ├── service.py       The full pipeline: schema → prompt → LLM → validate → execute
│       │   ├── schemas.py       Pydantic request and response models
│       │   └── history.py       In-memory query history (last 50 entries)
│       │
│       └── health/
│           └── router.py        GET /api/health — DB connectivity check
│
├── create_db.py                 Schema creation + seed data (25 employees, 124 sales, 192 expenses)
├── company.db                   SQLite database included for immediate use
├── main.py                      Single entry point — starts backend and frontend together
├── pyproject.toml
└── uv.lock
```

---

## Getting started

**Prerequisites:** Python 3.11+, Node.js 18+, a Mistral AI API key

```bash
# Clone
git clone https://github.com/qasim-mehar/text-to-SQL
cd text-to-SQL

# Backend setup
pip install uv
uv pip install -r requirements.txt

# Environment
cp .env.example .env
# Add your MISTRAL_API_KEY to .env

# Create and seed the database
python create_db.py --seed

# Start everything
python main.py
```

Backend runs at `http://localhost:8000`
Frontend runs at `http://localhost:5173`
API docs at `http://localhost:8000/docs`

---

## API reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/query` | Submit a question, get SQL + results |
| `GET` | `/api/schema` | Returns all tables and columns |
| `GET` | `/api/history` | Last 20 queries with outcomes |
| `GET` | `/api/health` | DB connectivity + model status |

**POST /api/query request:**
```json
{ "question": "Who are the top 3 highest paid employees?" }
```

**Response:**
```json
{
  "sql": "SELECT e.first_name, e.last_name, e.salary, d.department_name FROM employees e JOIN departments d ON e.department_id = d.department_id ORDER BY e.salary DESC LIMIT 3;",
  "data": [...],
  "error": null,
  "row_count": 3,
  "execution_time_ms": 312.4
}
```

---

## The database

The included `company.db` has 6 tables designed to produce interesting analytics results:

```
departments   6 rows    Finance intentionally has zero expenses (tests LEFT JOIN + NULL)
employees    25 rows    3-level management hierarchy, 1 true orphan (no manager, no reports)
projects      7 rows    Mixed statuses across two departments
sales       124 rows    All 12 months of 2024, 5 sales reps, 3 regions
expenses    192 rows    6 categories with realistic amount ranges per category
```

The data is shaped to make every test query meaningful. Laura Anderson is clearly the top sales rep. Kevin Taylor is the orphan employee. The Finance department has employees but zero expenses. Every sales rep covered all three regions. These are not accidents — they were put there to test specific SQL patterns.

---
---

## Questions worth testing

These exercise different SQL patterns and will reveal any remaining accuracy gaps:

```
Simple aggregation
  "How many employees are in each department?"
  "What is the total expenses per department in 2024?"

Window functions
  "Rank employees by salary within each department."
  "List employees earning above their department average, with the difference."

Pre-aggregation (the hard ones)
  "Which sales reps generated more revenue than their department's total expenses in 2024?"
  "Which department has the highest sales-to-expense ratio?"

Hierarchy / self-joins
  "Show each employee's 2-level management chain."
  "Find employees whose salary is higher than their direct manager's salary."

NULL handling
  "List all departments that have employees but zero recorded expenses in 2024."
  "Show all employees who have no manager and are not a manager of anyone."

Boss level
  "For each department, show the highest paid employee, the lowest paid, the gap between them,
   and whether 2024 expenses exceeded their combined salaries."
```

---

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///company.db` | SQLAlchemy connection string |
| `LLM_MODEL` | `mistral-medium-3-5` | Mistral model name |
| `MISTRAL_API_KEY` | required | Your Mistral AI API key |
| `MAX_ROWS` | `500` | Maximum rows returned per query |
| `MAX_RETRIES` | `2` | Self-correction retry attempts |
| `RATE_LIMIT_PER_MINUTE` | `10` | Requests per IP per minute |

---

## What is next

The current build is a solid foundation. Things worth adding:

- Support for PostgreSQL and MySQL (the pipeline is DB-agnostic except for `strftime` syntax)
- Query result caching for identical questions
- A schema change listener that rebuilds the DDL cache when tables are modified
- Export to CSV directly from the results table
- LangSmith tracing for debugging what the LLM saw at each retry

---

<div align="center">

Built by **Qasim Ali** as part of learning LangChain, LCEL, and production-grade AI pipeline engineering.

[LinkedIn](https://linkedin.com/in/qasim-mehr) &nbsp;&nbsp; [GitHub](https://github.com/qasim-mehar)

<sub>Python 100% &nbsp;|&nbsp; MIT License</sub>

</div>