from fastapi import FastAPI

from app.api.query import router as query_router
from app.api.rfid import router as rfid_router
from app.core.config import settings
from app.core.exceptions import add_exception_handlers
from app.core.logging_config import configure_logging


configure_logging()

app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
    version="1.0.0",
)

add_exception_handlers(app)
app.include_router(rfid_router)
app.include_router(query_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
