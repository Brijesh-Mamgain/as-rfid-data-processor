"""Pydantic models for the Natural Language Query endpoint."""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=5,
        max_length=500,
        examples=["How many valid RFID scans happened today?"],
    )


class QueryResponse(BaseModel):
    """Unified response for scalar counts, tabular data, and time-series charts.

    ``type`` tells the client how to render the result:

    * ``"scalar"``      – single number/value; use ``value`` for a count badge or KPI card.
    * ``"time_series"`` – rows contain at least one date/time column and one numeric column;
                          suitable for line or bar charts.
    * ``"tabular"``     – generic table data.

    Chart / trend consumers should look for date-like columns (``scan_date``,
    ``scan_hour``, ``day``, ``month``, …) as the X-axis and numeric columns
    as Y-axis series.
    """

    question: str
    sql: str = Field(description="The generated T-SQL SELECT that produced this result.")
    type: Literal["scalar", "time_series", "tabular"] = Field(
        description="Rendering hint for the client."
    )
    count: int = Field(description="Number of rows returned by the query.")
    columns: list[str] = Field(description="Ordered list of column names.")
    value: Optional[Any] = Field(
        default=None,
        description="Populated only when type=='scalar'. The single result value.",
    )
    rows: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Result rows as dicts. Empty when type=='scalar' (see value).",
    )
