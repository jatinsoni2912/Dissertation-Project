import json
import os
import uuid
import shutil
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

def save(username: str, conv: dict):
    path = conv_path(username, conv["id"])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(conv, f, indent=2, ensure_ascii=False)

def get_all_users() -> List[str]:
    """Return all usernames (directory names under conversations/)."""
    os.makedirs(CONV_DIR, exist_ok=True)
    return sorted(
        d for d in os.listdir(CONV_DIR)
        if os.path.isdir(os.path.join(CONV_DIR, d))
    )


def create_user(username: str):
    user_dir(username.strip())


def delete_user(username: str):
    path = os.path.join(CONV_DIR, username)
    if os.path.exists(path):
        shutil.rmtree(path)