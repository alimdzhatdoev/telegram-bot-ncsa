import json
from pathlib import Path
from datetime import datetime

EVENTS_PATH = Path("data/events.json")

def load_events():
    with open(EVENTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_events(events: list):
    with open(EVENTS_PATH, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)

def get_event_titles():
    return [event["title"] for event in load_events()]

def get_event_by_id(event_id: int):
    events = load_events()
    return next((e for e in events if e["id"] == event_id), None)

def get_next_event_id():
    events = load_events()
    if not events:
        return 1
    return max(e["id"] for e in events) + 1

def format_date(date_str: str) -> str:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d.%m.%Y")
    except ValueError:
        return date_str  # если что-то пошло не так — покажем как есть
