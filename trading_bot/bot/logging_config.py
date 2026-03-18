"""Configure structured JSON logging for the trading bot."""
import logging
import os
import json
from datetime import datetime


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
        }
        # Include structured fields when provided via 'extra'
        for key in ("event", "params", "response", "orderId", "clientOrderId"):
            if hasattr(record, key):
                val = getattr(record, key)
                if val is not None:
                    try:
                        payload[key] = val
                    except Exception:
                        payload[key] = str(val)

        # If exception info is present, include stack trace
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    logs_dir = os.path.join(base_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    log_path = os.path.join(logs_dir, "bot.log")

    # Root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # File handler with JSON formatter
    fh = logging.FileHandler(log_path)
    fh.setLevel(logging.INFO)
    fh.setFormatter(JsonFormatter())
    logger.addHandler(fh)

    # Console handler with simple formatting for developer convenience
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(ch)

