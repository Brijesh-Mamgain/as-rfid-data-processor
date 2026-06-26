import logging
import sys


def configure_logging() -> None:
    # force=True removes any handlers uvicorn already attached to the root
    # logger before this is called, ensuring our format and level take effect.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )
