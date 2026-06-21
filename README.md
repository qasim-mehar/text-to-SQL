<div align="center">

# 🧠 QueryBridge , Talk to Your Database Like a Human

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat&logo=sqlite&logoColor=white)](https://sqlite.org)
[![Mistral AI](https://img.shields.io/badge/Mistral_AI-orange?style=flat&logo=openai&logoColor=white)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Turn plain English questions into accurate, safe SQL queries. No SQL knowledge required.**

<img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Magic%20Wand.png" width="80" />

</div>

---

## 🎯 The Problem We Actually Faced

Let's be honest, SQL is powerful, but it's also a pain.

> *"Hey, can you tell me which sales reps outperformed their department's total expenses this year?"*

Sounds simple, right? But translating that into SQL means:
- Remembering which tables hold what
- Knowing when to `JOIN` vs when to `LEFT JOIN`
- Avoiding the **fan-out trap** (ever summed sales and expenses in one query and got numbers that made no sense?)
- Writing `strftime('%Y', ...)` because SQLite date handling is... special

And that's for *one* question. Now imagine your non-technical teammate asking 20 of these a day. Or worse — you spending 15 minutes writing a query that should take 15 seconds.

**We built QueryBridge because we were tired of being human SQL translators.**

---

## ✨ Our Solution: An AI That *Actually* Understands Your Schema

QueryBridge isn't just "throw a prompt at an LLM and hope." It's a carefully engineered pipeline that treats SQL generation like the precision craft it is.

### 🏗️ Architecture at a Glance

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   You Ask:      │     │  QueryBridge     │     │   Your Data     │
│  "Who are the   │────▶│  Pipeline        │────▶│   (SQLite DB)   │
│   top earners?" │     │                  │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         ▼                     ▼                     ▼
    ┌─────────┐         ┌──────────┐         ┌──────────┐
    │ Schema  │         │ Few-Shot │         │ Anti-    │
    │ Intros. │         │ Examples │         │ Patterns │
    │ (DDL)   │         │ (8 ex.)  │         │ Rules    │
    └─────────┘         └──────────┘         └──────────┘
         │                     │                     │
         └─────────────────────┼─────────────────────┘
                               ▼
                    ┌──────────────────┐
                    │   Mistral AI     │
                    │   (mistral-med)  │
                    └──────────────────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │  Self-Correcting │
                    │  Retry Loop      │
                    │  (max 2 retries) │
                    └──────────────────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │  Validated SQL   │
                    │  (SELECT only)   │
                    └──────────────────┘
```

---

## 🛡️ What Makes This Different

Most text-to-SQL demos are basically: *"Here's a schema, LLM, go wild."*

We don't do that here. Here's what we actually built in:

| Feature | Why It Matters |
|---------|--------------|
| 🧩 **DDL Schema Injection** | We feed the LLM actual `CREATE TABLE` statements, not JSON. LLMs understand DDL way better. |
| 📚 **8 Curated Few-Shot Examples** | Pre-aggregation, window functions, CTEs, self-joins — we taught the model *how* we want queries written. |
| 🚫 **Anti-Pattern Rules** | Hard-coded rules in the system prompt prevent fan-out joins, `SELECT *`, and unsafe division. |
| 🔒 **Destructive Query Block** | `DROP`, `DELETE`, `UPDATE`, `INSERT`? Nope. The validator rejects them before they touch your DB. |
| 🔄 **Self-Correcting Loop** | If SQL fails, we feed the error *back* into the prompt and retry — no human intervention needed. |
| 🏷️ **Role-Aware Filtering** | Ask for "sales reps" and it actually filters by `job_title`, not just anyone who happens to have sales records. |

---

## 🚀 Tech Stack

<div align="center">

| Layer | Tech |
|-------|------|
| 🧠 LLM | **Mistral AI** (mistral-medium-3-5) via LangChain |
| ⚡ Backend | **FastAPI** + SQLAlchemy + Pydantic |
| 🎨 Frontend | **React 18** + TypeScript + Tailwind CSS + shadcn/ui |
| 💾 Database | **SQLite** (lightweight, portable, perfect for demos) |
| 🔧 Tooling | uv, Vite, PostCSS |

</div>

---

## 🎬 See It In Action

```
You: "Which department has the highest sales-to-expense ratio in 2024?"

QueryBridge thinks...
✓ Detects multi-table aggregation needed
✓ Pre-aggregates sales and expenses separately (no fan-out!)
✓ Uses CTEs for readability
✓ Wraps denominator in NULLIF (no division by zero)
✓ Validates — safe to run
✓ Executes — returns clean JSON

Results: [{"department_name": "Sales", "ratio": 4.82}, ...]
```

---

## 📂 Project Structure

```
text-to-sql-query/
├── 📁 backend/
│   └── 📁 app/
│       ├── 📁 core/              # Config, DB engine, exceptions
│       ├── 📁 features/
│       │   └── 📁 text_to_sql/   # Router, service, schemas, deps
│       └── main.py               # FastAPI bootstrap
├── 📁 frontend/
│   ├── 📁 src/
│   │   ├── 📁 components/        # UI primitives (shadcn)
│   │   ├── 📁 features/
│   │   │   ├── 📁 landing/       # Hero, features, CTA
│   │   │   └── 📁 query/         # Query input, SQL preview, results
│   │   ├── App.tsx
│   │   └── main.tsx
│   └── package.json
├── create_db.py                  # Seed data generator
├── company.db                    # Sample database
└── README.md                     # You are here 🙃
```

---

## 🏃 Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/yourusername/text-to-sql-query.git
cd text-to-sql-query
```

### 2. Backend

```bash
cd backend
uv pip install -r requirements.txt

# Set your Mistral API key
cp .env.example .env
# Edit .env: MISTRAL_API_KEY=your_key_here

uvicorn app.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

### 4. Open `http://localhost:5173` and start asking questions! 🎉

---

## 🧪 Example Queries to Try

> 💡 *These are the exact kinds of questions that used to require 10 minutes of SQL writing. Now they take 10 seconds.*

- "How many employees are in each department?"
- "List employees earning above their department average, with the difference."
- "Show each employee's 2-level management chain."
- "Which sales reps generated more revenue than their department's total expenses in 2024?"
- "Rank employees by salary within each department."
- "Show monthly sales totals for 2024."

---

## 🧠 Real Talk: Why This Works

We didn't just slap a LangChain wrapper on an API call. We spent time understanding **why** text-to-SQL fails in production:

1. **Fan-out joins** — joining two fact tables without pre-aggregation gives you nonsense sums. We literally wrote a "WRONG vs CORRECT" example in the prompt.

2. **Window functions + self-joins** — LLMs love combining these and creating row explosions. We taught it to use CTEs instead.

3. **Division by zero** — Classic SQLite runtime error. We wrap every denominator in `NULLIF(..., 0)`.

4. **Role ambiguity** — Just because someone has a sales record doesn't make them a "sales rep." We enforce `job_title` filtering.

This is the kind of thing you only learn after watching an LLM generate broken SQL for the 50th time. 😅

---

## 🤝 Contributing

Found a query that breaks it? We'd love to know! Open an issue with:
- Your natural language question
- The SQL it generated
- What you expected

PRs welcome. Keep it friendly. 💙

---

## 📜 License

MIT — do whatever you want, just don't blame us if your LLM hallucinates a `DROP TABLE`.

*(Kidding — our validator won't let it through anyway.)* 🔒

---

<div align="center">

**Built with ☕, 🧠, and a healthy distrust of `SELECT *`.**

⭐ Star us if this saved you from writing SQL today!

</div>
