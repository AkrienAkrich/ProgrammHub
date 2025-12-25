# main.py

import os
import json
from pathlib import Path

import webview  # pip install pywebview

# Ваши импорты
from core.models import Game
from core.storage import save_games, load_settings, save_settings  # Добавил save_settings

from scanner.steam import scan_steam
from scanner.epic import scan_epic
from scanner.system import scan_system

from scanner.steam import download_cover  # Функция скачивания обложки для Steam

from core.launcher import start_game

from utils.paths import get_data_path

# Путь к фронтенду
FRONTEND_DIR = Path(__file__).parent / "frontend"
INDEX_HTML = FRONTEND_DIR / "index.html"

if not INDEX_HTML.exists():
    raise FileNotFoundError(
        f"Не найден файл {INDEX_HTML}\n"
        "Убедитесь, что в корне проекта есть папка 'frontend' с файлами:\n"
        "  - index.html\n  - style.css\n  - script.js"
    )

# Глобальный список игр в памяти
all_games = []

def full_scan():
    """Полное сканирование всех источников"""
    global all_games
    print("Выполняется полное сканирование программ...")
    all_games = []

    # Сканируем Steam (с обложками)
    steam_games = scan_steam()
    print(f"Найдено {len(steam_games)} игр в Steam.")
    for game in steam_games:
        if game.cover is None and game.id:  # На всякий случай — докачиваем обложку
            game.cover = download_cover(game.id)
    all_games.extend(steam_games)

    # Epic
    epic_games = scan_epic()
    print(f"Найдено {len(epic_games)} игр в Epic.")
    all_games.extend(epic_games)

    # System
    system_games = scan_system()
    print(f"Найдено {len(system_games)} программ в System.")
    all_games.extend(system_games)

    # Сохраняем в кэш
    save_games(all_games)
    print(f"Сканирование завершено. Всего {len(all_games)} программ.")

def load_from_cache():
    """Загружает игры из games.json, если он существует и не пустой"""
    global all_games
    cache_path = get_data_path("games.json")
    if not os.path.exists(cache_path):
        print("Кэш games.json не найден.")
        return False

    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not data:
            print("Кэш games.json пустой.")
            return False

        all_games = [Game.from_dict(item) for item in data]
        print(f"Загружено {len(all_games)} программ из кэша.")
        return True
    except Exception as e:
        print(f"Ошибка чтения кэша games.json: {e}")
        return False

def assign_unassigned():
    """Присваивает нераспределённые игры к категориям по source"""
    settings = load_settings()
    categories = settings['categories']
    assigned_ids = set(id for cat_list in categories.values() for id in cat_list)

    changed = False
    for game in all_games:
        if game.id not in assigned_ids:
            cat_key = game.source.capitalize()
            if cat_key in categories:
                categories[cat_key].append(game.id)
                assigned_ids.add(game.id)
                changed = True

    if changed:
        print("Обновлены категории в settings.json.")
        save_settings(settings)

def load_or_scan():
    """Основная логика загрузки при старте"""
    if not load_from_cache():
        full_scan()
    assign_unassigned()
    if not all_games:
        print("Внимание: Нет программ после загрузки/сканирования. Проверьте установку Steam/Epic или реестр.")

class Api:
    """API, доступный из JavaScript через window.pywebview.api"""

    def getCategories(self):
        settings = load_settings()
        cats = ["Все"] + list(settings['categories'].keys())
        return [{"name": cat} for cat in cats]

    def getPrograms(self):
        settings = load_settings()
        programs = []
        for game in all_games:
            # Определяем категорию (первая, где id есть, или по source)
            category = next((cat for cat, ids in settings['categories'].items() if game.id in ids), game.source.capitalize())

            # Обложка
            cover_url = ""
            if game.cover and os.path.exists(game.cover):
                cover_url = f"file://{Path(game.cover).resolve()}"

            programs.append({
                "name": game.name,
                "path": game.path,
                "cover": cover_url,
                "category": category,
                "source": game.source,
                "id": game.id
            })
        print(f"Возвращено {len(programs)} программ в JS.")
        return programs

    def launchProgram(self, path: str):
        target_game = next((game for game in all_games if game.path == path), None)
        if target_game:
            try:
                start_game(target_game)
                return {"success": True}
            except Exception as e:
                print(f"Ошибка запуска {path}: {e}")
                return {"success": False, "error": str(e)}
        return {"success": False, "error": "Игра не найдена"}

    def rescan(self):
        full_scan()
        assign_unassigned()
        return {"success": True, "count": len(all_games)}

# ==================== ЗАПУСК ====================
if __name__ == "__main__":
    load_or_scan()

    api = Api()

    window = webview.create_window(
        title="ProgrammHub",
        url=str(INDEX_HTML),
        js_api=api,
        width=1280,
        height=800,
        resizable=True,
        min_size=(1000, 600),
        background_color="#0e1117",
        text_select=False,
        frameless=False,
    )

    webview.start(debug=False)  # debug=True для DevTools