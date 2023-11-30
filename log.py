import logging
from datetime import datetime, timezone

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S UTC",
)
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S UTC",
)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S UTC",
)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def d(i: int) -> None:
    """debug"""
    log.info("***%s***", str(i))


def current_utc_date_int() -> int:
    """current_utc_date_int"""
    return int(datetime.now(timezone.utc).timestamp())


def int_utc_to_str(utc_int_date: int, format="%Y-%m-%d %H:%M:%S UTC") -> str:
    """int_utc_to_str"""
    utc_datetime = datetime.utcfromtimestamp(utc_int_date)
    return utc_datetime.strftime(format)
