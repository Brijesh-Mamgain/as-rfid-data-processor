"""Natural Language → SQL → Results service.

Flow
────
1. Receive a plain-English question.
2. Send it to Azure OpenAI (GPT-4o) with the full DB schema as context.
3. Extract and safety-validate the generated SQL (SELECT-only allow-list).
4. Execute against Azure SQL via AzureSQLClient.execute_query().
5. Infer the best response shape (scalar, tabular, time-series) so the
   caller can decide how to render the data (count badge, table, chart).
"""

from __future__ import annotations

import logging
import re
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from openai import AzureOpenAI

from app.core.config import settings
from app.integrations.azure_sql import AzureSQLClient
from app.services.schema_context import DB_SCHEMA_CONTEXT

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Prompt
# ──────────────────────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = f"""
You are an expert Microsoft SQL Server (Azure SQL / T-SQL) assistant.

Given the schema below, convert the user's natural-language question into a
valid T-SQL SELECT query.

STRICT RULES:
1. Output ONLY the raw SQL — no markdown fences, no prose, no explanation.
2. The query MUST start with SELECT. Never use INSERT, UPDATE, DELETE, DROP,
   TRUNCATE, ALTER, CREATE, EXEC, EXECUTE, GRANT, REVOKE, or MERGE.
3. Always prefix table names with the dbo schema: dbo.<table>.
4. Use GETUTCDATE() for "now". Use CAST(col AS DATE) to strip time.
5. For trend / time-series questions, include a date or datetime column
   so the caller can plot the data. Use aliases like scan_date, scan_hour.
6. Limit result sets to at most 1 000 rows using TOP or WHERE filters unless
   the user explicitly asks for all records.
7. Do NOT use subqueries that reference outer aliases in FROM clauses in a way
   incompatible with SQL Server.

Schema:
{DB_SCHEMA_CONTEXT}
""".strip()

# ──────────────────────────────────────────────────────────────────────────────
# SQL safety guard
# ──────────────────────────────────────────────────────────────────────────────

_SELECT_RE = re.compile(r"^\s*SELECT\b", re.IGNORECASE)
_DANGER_RE = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|TRUNCATE|ALTER|CREATE|EXEC|EXECUTE|GRANT|REVOKE|MERGE|OPENROWSET|BULK)\b",
    re.IGNORECASE,
)
_COMMENT_RE = re.compile(r"(--[^\n]*|/\*.*?\*/)", re.DOTALL)


def _sanitize_and_validate(sql: str) -> str:
    """Strip leading/trailing whitespace and markdown fences, then validate.

    Raises ``ValueError`` if the query is not a safe SELECT statement.
    """
    # Strip ```sql … ``` fences that the model sometimes adds despite the prompt
    sql = re.sub(r"^```[a-z]*\s*", "", sql.strip(), flags=re.IGNORECASE)
    sql = re.sub(r"\s*```$", "", sql.strip())
    sql = sql.strip()

    # Remove inline/block comments before danger-keyword scan
    cleaned = _COMMENT_RE.sub(" ", sql)

    if not _SELECT_RE.match(cleaned):
        raise ValueError(f"Generated query does not start with SELECT: {sql[:120]!r}")

    danger = _DANGER_RE.search(cleaned)
    if danger:
        raise ValueError(
            f"Generated query contains disallowed keyword '{danger.group()}': {sql[:120]!r}"
        )

    return sql


# ──────────────────────────────────────────────────────────────────────────────
# Response shape inference
# ──────────────────────────────────────────────────────────────────────────────

_DATE_LIKE_COLS = re.compile(
    r"(date|day|hour|week|month|year|timestamp|period|time)", re.IGNORECASE
)

_SERIALIZABLE_TYPES = (str, int, float, bool, Decimal, date, datetime, type(None))


def _make_serializable(value: Any) -> Any:
    """Convert pyodbc-returned types that are not JSON-serializable."""
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def _serialize_rows(rows: list[dict]) -> list[dict]:
    return [
        {k: _make_serializable(v) for k, v in row.items()}
        for row in rows
    ]


def _infer_response_type(rows: list[dict], sql: str) -> str:
    """Return one of: 'scalar', 'time_series', 'tabular'."""
    if not rows:
        return "tabular"
    if len(rows) == 1 and len(rows[0]) == 1:
        return "scalar"
    columns = list(rows[0].keys())
    has_time_col = any(_DATE_LIKE_COLS.search(col) for col in columns)
    has_numeric = any(
        isinstance(v, (int, float, Decimal))
        for v in rows[0].values()
        if v is not None
    )
    if has_time_col and has_numeric:
        return "time_series"
    return "tabular"


# ──────────────────────────────────────────────────────────────────────────────
# Service
# ──────────────────────────────────────────────────────────────────────────────

class NLQueryService:
    """Translates a natural-language question into SQL, executes it, and returns
    a structured response ready for rendering as a count, table, or chart."""

    def __init__(self) -> None:
        if not settings.azure_openai_endpoint or not settings.azure_openai_api_key:
            raise RuntimeError(
                "AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY must be configured."
            )
        self._llm = AzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
        )

    # ── public ──────────────────────────────────────────────────────────────

    def query(self, question: str) -> dict:
        """Run the full NL → SQL → DB pipeline.

        Returns a dict with keys:
            question    – the original user question
            sql         – the generated T-SQL
            type        – 'scalar' | 'time_series' | 'tabular'
            count       – number of rows returned
            rows        – list[dict] of results (empty for scalar, see 'value')
            value       – scalar value when type == 'scalar', else None
            columns     – ordered list of column names
        """
        sql = self._generate_sql(question)
        logger.info("nl_query sql=%s", sql)

        db = AzureSQLClient()
        raw_rows = db.execute_query(sql, max_rows=settings.nl_query_max_rows)
        rows = _serialize_rows(raw_rows)

        response_type = _infer_response_type(rows, sql)
        columns = list(rows[0].keys()) if rows else []

        scalar_value = None
        if response_type == "scalar" and rows:
            scalar_value = list(rows[0].values())[0]
            rows = []  # no need to duplicate in both fields

        return {
            "question": question,
            "sql": sql,
            "type": response_type,
            "count": len(raw_rows),
            "columns": columns,
            "value": scalar_value,
            "rows": rows,
        }

    # ── private ─────────────────────────────────────────────────────────────

    def _generate_sql(self, question: str) -> str:
        response = self._llm.chat.completions.create(
            model=settings.azure_openai_deployment,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
            temperature=0,
            max_tokens=600,
        )
        raw_sql = response.choices[0].message.content or ""
        return _sanitize_and_validate(raw_sql)
