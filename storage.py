import json
import os

from config import DATA_FILE, P1_KEY, P2_KEY


def load_data():
    if not os.path.exists(DATA_FILE):
        return {
            P1_KEY: {"score": 0, "wishes": 0},
            P2_KEY: {"score": 0, "wishes": 0},
            "places": [],
        }
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {
            P1_KEY: {"score": 0, "wishes": 0},
            P2_KEY: {"score": 0, "wishes": 0},
            "places": [],
        }

    if "places" not in data or not isinstance(data["places"], list):
        data["places"] = []

    return data


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
