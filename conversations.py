import json
import os
import uuid
from datetime import datetime
from typing import Optional, List, Dict

CONV_DIR = os.path.join(os.path.dirname(__file__), "conversations")

def user_dir(username: str) -> str:
    path = os.path.join(CONV_DIR, username)
    os.makedirs(path, exist_ok=True)
    return path

def conv_path(username: str, conv_id: str) -> str:
    return os.path.join(user_dir(username), f"{conv_id}.json")


def load(username: str, conv_id: str) -> Optional[Dict]:
    path = conv_path(username, conv_id)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)