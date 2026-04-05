import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ABOUT_JSON_PATH = os.path.join(BASE_DIR, "config", "about.json")

def load_about_data():
    with open(ABOUT_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
