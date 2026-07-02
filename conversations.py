import json
import os
import uuid
import shutil
from datetime import datetime
from typing import Optional, List, Dict

CONV_DIR = os.path.join(os.path.dirname(__file__), "conversations")

def user_dir(username):
    path = os.path.join(CONV_DIR, username)
    os.makedirs(path, exist_ok=True)
    return path

def conv_path(username, conv_id):
    return os.path.join(user_dir(username), f"{conv_id}.json")


def load(username, conv_id):
    path = conv_path(username, conv_id)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def save(username, conv):
    path = conv_path(username, conv["id"])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(conv, f, indent=2, ensure_ascii=False)

def get_all_users():
    """Return all usernames (directory names under conversations/)."""
    os.makedirs(CONV_DIR, exist_ok=True)
    return sorted(
        d for d in os.listdir(CONV_DIR)
        if os.path.isdir(os.path.join(CONV_DIR, d))
    )


def create_user(username):
    user_dir(username.strip())


def delete_user(username):
    path = os.path.join(CONV_DIR, username)
    if os.path.exists(path):
        shutil.rmtree(path)

def new_conversation(username):
    conv = {
        "id":         uuid.uuid4().hex[:12],
        "title":      "New conversation",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "messages":   [],
    }
    save(username, conv)
    return conv

def get_all_conversations(username):
    udir = user_dir(username)
    convs = []
    for fname in os.listdir(udir):
        if not fname.endswith(".json"):
            continue
        try:
            with open(os.path.join(udir, fname), encoding="utf-8") as f:
                c = json.load(f)
            convs.append({
                "id":         c["id"],
                "title":      c.get("title", "Untitled"),
                "created_at": c.get("created_at", ""),
                "updated_at": c.get("updated_at", ""),
                "msg_count":  len(c.get("messages", [])),
            })
        except Exception:
            continue
    return sorted(convs, key=lambda x: x["updated_at"], reverse=True)

def load_conversation(username: str, conv_id: str) -> Optional[Dict]:
    return load(username, conv_id)

def add_message(
    username:            str,
    conv_id:             str,
    query:               str,
    sql:                 str,
    approach:            str,
    model:               str,
    row_count:           int,
    is_count:            bool,
    fixes_applied:       list,
    input_method:        str   = "text",
    asr_transcript:      str   = None,
    asr_confidence:      float = None,
    area_filter_active:  bool  = False,
    area_filter_geojson: dict  = None,
) -> Dict:
    
    conv = load(username, conv_id)
    if conv is None:
        conv = new_conversation(username)

    msg = {
        "query":               query,
        "sql":                 sql,
        "approach":            approach,
        "model":               model,
        "row_count":           row_count,
        "is_count":            is_count,
        "fixes_applied":       fixes_applied or [],
        "input_method":        input_method,
        "asr_transcript":      asr_transcript,
        "asr_confidence":      asr_confidence,
        "area_filter_active":  area_filter_active,
        "area_filter_geojson": area_filter_geojson,
        "timestamp":           datetime.now().isoformat(),
    }
    conv["messages"].append(msg)
    conv["updated_at"] = msg["timestamp"]

    if len(conv["messages"]) == 1:
        conv["title"] = query[:60] + ("…" if len(query) > 60 else "")

    save(username, conv)
    return conv

def delete_conversation(username, conv_id):
    path = conv_path(username, conv_id)
    if os.path.exists(path):
        os.remove(path)


def get_user_stats(username):
    convs_meta = get_all_conversations(username)
    total_msgs = sum(c["msg_count"] for c in convs_meta)
    voice = 0
    for cm in convs_meta:
        conv = load_conversation(username, cm["id"])
        if conv:
            voice += sum(1 for m in conv["messages"]
                         if m.get("input_method") == "voice")
    return {
        "conversations": len(convs_meta),
        "total_queries": total_msgs,
        "voice_queries": voice,
    }
