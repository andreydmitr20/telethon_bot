""" get constants from .env"""
import os
import json
from dotenv import load_dotenv

CONFIG_FILENAME = ".env"
load_dotenv(CONFIG_FILENAME)

# KEYS_JSON_PATH = "./.keys.json"


def load_dict(path: str) -> dict:
    """load_dict"""
    if os.path.exists(path):
        try:
            with open(path, "r") as file:
                text = file.read()
            return json.loads(text)
        except:
            pass
    return {}


# from config import config
class config:
    """common config constants"""

    filename = CONFIG_FILENAME

    bot_token: str = os.getenv("bot_token")
    phone: str = os.getenv("phone")
    api_id: str = os.getenv("api_id")
    api_hash: str = os.getenv("api_hash")
