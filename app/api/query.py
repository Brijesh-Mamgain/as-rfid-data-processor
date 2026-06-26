"""Natural Language Query API router.

POST /query
───────────
Accepts a plain-English question and returns SQL query results shaped for
display as a count badge, data table, or trend chart (line / bar graph).

Authentication
──────────────
Reuses the same Bearer token guard as the RFID endpoints.

Response shapes
───────────────
type == "scalar"      → single KPI value  (e.g. total scan count)
type == "time_series" → rows with a date/time column + numeric columns (chart-ready)
type == "tabular"     → general table result
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app.api.rfid import _verify_rfid_api_token
from app.models.query import QueryRequest, QueryResponse
from app.services.nl_query_service import NLQueryService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/query",
    tags=["Natural Language Query"],
    dependencies=[Depends(_verify_rfid_api_token)],
)


@router.post(
    "",
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Query Data in Natural language",
    description=(
        "Convert a plain-English question into T-SQL, execute it against the "
        "RFID database, and return results shaped for counts, tables, or charts."
    ),
)
def natural_language_query(body: QueryRequest) -> QueryResponse:
    try:
        service = NLQueryService()
    except RuntimeError as exc:
        logger.error("nl_query misconfigured: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    try:
        result = service.query(body.question)
    except ValueError as exc:
        # Safety-guard rejected the generated SQL
        logger.warning("nl_query blocked: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not generate a safe query: {exc}",
        ) from exc
    except Exception as exc:
        logger.exception("nl_query execution error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{type(exc).__name__}: {exc}",
        ) from exc

    logger.info(
        "nl_query_complete type=%s rows=%s question=%r",
        result["type"],
        result["count"],
        body.question,
    )

    return QueryResponse(**result)
