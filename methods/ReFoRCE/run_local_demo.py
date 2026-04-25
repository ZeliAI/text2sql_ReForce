import argparse
import csv
import json
import os
import re
import sqlite3
from pathlib import Path

from chat import BaseChat, GPTChat


class MockChat(BaseChat):
    def get_response(self, prompt) -> str:
        self.messages.append({"role": "user", "content": prompt})
        response = """```sql
SELECT department, ROUND(AVG(salary), 2) AS avg_salary
FROM employees
GROUP BY department
ORDER BY avg_salary DESC;
```"""
        self.messages.append({"role": "assistant", "content": response})
        return response


def extract_sql(text: str) -> str:
    matches = re.findall(r"```sql\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
    if matches:
        return matches[-1].strip()
    cleaned = text.strip()
    if cleaned.endswith(";"):
        return cleaned
    raise ValueError("No SQL block found in model response.")


def tokenize(text: str) -> set[str]:
    return {token.lower() for token in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", text)}


def create_demo_db(sqlite_path: Path) -> None:
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(sqlite_path) as conn:
        conn.executescript(
            """
            DROP TABLE IF EXISTS employees;
            DROP TABLE IF EXISTS departments;

            CREATE TABLE departments (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                region TEXT NOT NULL
            );

            CREATE TABLE employees (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                salary REAL NOT NULL,
                hired_at TEXT NOT NULL
            );

            INSERT INTO departments VALUES
                (1, 'Sales', 'North'),
                (2, 'Engineering', 'West'),
                (3, 'Finance', 'East');

            INSERT INTO employees VALUES
                (1, 'Alice', 'Sales', 95000, '2021-02-14'),
                (2, 'Bob', 'Sales', 87000, '2020-08-01'),
                (3, 'Cathy', 'Engineering', 135000, '2019-06-20'),
                (4, 'Dan', 'Engineering', 142000, '2022-01-10'),
                (5, 'Eve', 'Finance', 99000, '2021-11-03');
            """
        )


def list_tables(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    return [row[0] for row in rows]


def build_schema(sqlite_path: Path, question: str, max_tables: int) -> str:
    question_tokens = tokenize(question)
    table_blocks = []
    with sqlite3.connect(sqlite_path) as conn:
        for table in list_tables(conn):
            columns = conn.execute(f'PRAGMA table_info("{table}")').fetchall()
            column_names = [col[1] for col in columns]
            score = len(question_tokens & tokenize(" ".join([table] + column_names)))
            rows = conn.execute(f'SELECT * FROM "{table}" LIMIT 3').fetchall()
            table_blocks.append((score, table, columns, rows))

    table_blocks.sort(key=lambda item: (-item[0], item[1]))
    selected = table_blocks[:max_tables] if any(score for score, *_ in table_blocks) else table_blocks

    lines = ["The table structure information is:"]
    for _, table, columns, rows in selected:
        lines.append(f"Table full name: {table}")
        for _, name, col_type, *_ in columns:
            lines.append(f"Column name: {name} Type: {col_type}")
        if rows:
            col_names = [col[1] for col in columns]
            sample_rows = [dict(zip(col_names, row)) for row in rows]
            lines.append("Sample rows:")
            lines.append(json.dumps(sample_rows, ensure_ascii=False))
        lines.append("-" * 50)
    return "\n".join(lines)


def execute_sql(sqlite_path: Path, sql: str, csv_path: Path) -> str:
    with sqlite3.connect(sqlite_path) as conn:
        cur = conn.execute(sql)
        rows = cur.fetchall()
        headers = [desc[0] for desc in cur.description or []]

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    return csv_path.read_text(encoding="utf-8")


def build_prompt(schema: str, question: str) -> str:
    return f"""{schema}

Task: {question}

Please think step by step and answer only one complete SQL query in SQLite dialect.
Use only tables and columns shown in the schema.
Return the SQL inside one ```sql``` code block.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a tiny local Text-to-SQL ReFoRCE smoke test.")
    parser.add_argument("--sqlite", type=Path, default=Path("examples_local/local_demo/demo.sqlite"))
    parser.add_argument("--question", default="What is the average salary for each department?")
    parser.add_argument("--model", default=os.environ.get("LLM_MODEL", "gpt-4o-mini"))
    parser.add_argument("--temperature", type=float, default=float(os.environ.get("LLM_TEMPERATURE", "1")))
    parser.add_argument("--output_path", type=Path, default=Path("output/local-demo"))
    parser.add_argument("--max_iter", type=int, default=2)
    parser.add_argument("--max_tables", type=int, default=8)
    parser.add_argument("--mock", action="store_true", help="Use a deterministic local mock instead of calling an LLM.")
    args = parser.parse_args()

    if not args.sqlite.exists():
        create_demo_db(args.sqlite)

    chat = MockChat(args.model, temperature=args.temperature) if args.mock else GPTChat(model=args.model, temperature=args.temperature)
    schema = build_schema(args.sqlite, args.question, args.max_tables)
    prompt = build_prompt(schema, args.question)

    args.output_path.mkdir(parents=True, exist_ok=True)
    sql_path = args.output_path / "result.sql"
    csv_path = args.output_path / "result.csv"
    log_path = args.output_path / "log.json"

    attempts = []
    last_prompt = prompt
    for _ in range(args.max_iter + 1):
        response = chat.get_response(last_prompt)
        sql = extract_sql(response)
        try:
            csv_result = execute_sql(args.sqlite, sql, csv_path)
            sql_path.write_text(sql + "\n", encoding="utf-8")
            attempts.append({"sql": sql, "status": "ok", "csv": csv_result})
            break
        except Exception as exc:
            attempts.append({"sql": sql, "status": "error", "error": str(exc)})
            last_prompt = (
                f"The previous SQL failed with this SQLite error:\n{exc}\n\n"
                f"Previous SQL:\n```sql\n{sql}\n```\n\n"
                "Please correct it and return exactly one complete SQL query in a ```sql``` block."
            )

    log_path.write_text(json.dumps({"question": args.question, "schema": schema, "attempts": attempts}, indent=2), encoding="utf-8")

    if not attempts or attempts[-1]["status"] != "ok":
        raise SystemExit(f"Failed to produce executable SQL. See {log_path}")

    print(f"SQL saved to: {sql_path}")
    print(f"CSV saved to: {csv_path}")
    print(attempts[-1]["csv"])


if __name__ == "__main__":
    main()
