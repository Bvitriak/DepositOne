import json
import os

ABOUT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "about.json")


def get_about():
    with open(ABOUT_FILE, encoding="utf-8") as about_file:
        return json.load(about_file)
