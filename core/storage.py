# game_launcher/core/storage.py

import json
import os
from utils.paths import get_data_path, get_settings_path

def save_games(games):
    games_path = get_data_path("games.json")
    with open(games_path, "w", encoding="utf-8") as f:
        json.dump([g.to_dict() for g in games], f, indent=4, ensure_ascii=False)

def save_settings(settings):
    settings_path = get_settings_path()
    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)

def load_settings():
    settings_path = get_settings_path()
    default = {
        "scanners": {"steam": True, "epic": True, "system": True},
        "discord_rpc": True,
        "theme": "dark",
        "categories": {
            "Steam": [],
            "Epic": [],
            "System": [],
            "Custom": []
        }
    }
    if os.path.exists(settings_path):
        with open(settings_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            default.update(data)
    else:
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=4)
    return default