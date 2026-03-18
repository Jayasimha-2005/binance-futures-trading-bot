import os
from dotenv import load_dotenv
from binance.client import Client
from .logging_config import configure_logging
import logging


load_dotenv()
configure_logging()


def get_client():
    """Initialize and return a Binance client configured for USDT-M testnet.

    Loads API_KEY and API_SECRET from environment (.env) and sets the
    futures base URL to the testnet endpoint if provided via `BASE_URL`.
    """
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")
    if not api_key or not api_secret:
        raise ValueError("API_KEY and API_SECRET must be set in .env")

    base_url = os.getenv("BASE_URL")

    client = Client(api_key, api_secret)

    # If a BASE_URL is provided, attempt to set common client attributes
    # so futures requests will be sent to the testnet endpoint.
    if base_url:
        try:
            # common python-binance attributes across versions
            # Ensure futures path is present for USDT-M endpoints
            fut_url = base_url
            if "fapi" not in base_url:
                # prefer /fapi (REST futures) for python-binance
                fut_url = base_url.rstrip("/") + "/fapi"

            setattr(client, "FUTURES_URL", fut_url)
            setattr(client, "futures_url", base_url)
            setattr(client, "API_URL", base_url)
            setattr(client, "API_BASE_URL", base_url)
        except Exception:
            logging.debug("Could not set base URL attributes on client")

    logging.info("Binance client initialized (testnet futures). Base URL=%s", base_url)
    return client
