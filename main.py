# game_launcher/main.py

import os
import json  # ← Добавлено здесь
from utils.paths import get_data_path
from core.models import Game
from ui.app import App
from scanner.steam import scan_steam
from scanner.epic import scan_epic
from scanner.system import scan_system
from core.storage import save_games, save_settings, load_settings

def scan_and_save(settings):
    games = []
    if settings["scanners"].get("steam", True):
        games.extend(scan_steam())
    if settings["scanners"].get("epic", True):
        games.extend(scan_epic())
    if settings["scanners"].get("system", True):
        games.extend(scan_system())

    # Удаляем дубликаты
    seen = set()
    unique = []
    for g in games:
        key = (str(g.id), g.source)
        if key not in seen:
            seen.add(key)
            unique.append(g)
    return unique

def assign_categories(games, settings):
    # Очищаем базовые категории перед заполнением
    for base in ["Steam", "Epic", "System", "Custom"]:
        if base in settings["categories"]:
            settings["categories"][base] = []

    for game in games:
        cat = game.source.capitalize()
        if cat not in settings["categories"]:
            settings["categories"][cat] = []
        if str(game.id) not in settings["categories"][cat]:
            settings["categories"][cat].append(str(game.id))

    save_settings(settings)

if __name__ == "__main__":
    settings = load_settings()

    games_path = get_data_path("games.json")
    if not os.path.exists(games_path):
        print("Сканируем игры впервые...")
        games = scan_and_save(settings)
        save_games(games)
    else:
        # Загружаем игры из кэша
        with open(games_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            games = [Game.from_dict(g) for g in data]

    # Заполняем категории ДО создания окна
    assign_categories(games, settings)

    app = App(games, settings)
    app.mainloop()