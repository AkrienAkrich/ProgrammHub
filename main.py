# main.py

import os
import json
import time
from pathlib import Path
import subprocess

import webview

from core.models import Game
from core.storage import save_games, load_settings, save_settings
from scanner.steam import scan_steam
from scanner.epic import scan_epic
from scanner.system import scan_system
from scanner.steam import download_cover
from core.launcher import start_game  # На всякий случай оставляем, но используем свой метод
from utils.paths import get_data_path

FRONTEND_DIR = Path(__file__).parent / "frontend"
INDEX_HTML = FRONTEND_DIR / "index.html"

if not INDEX_HTML.exists():
    raise FileNotFoundError(f"Не найден {INDEX_HTML}. Создайте папку frontend с index.html, style.css, script.js")

all_games = []

def full_scan():
    global all_games
    print("Полное сканирование...")
    all_games = []
    steam_games = scan_steam()
    print(f"Steam: {len(steam_games)}")
    for g in steam_games:
        if g.cover is None and g.id:
            g.cover = download_cover(g.id)
    all_games.extend(steam_games)

    all_games.extend(scan_epic())
    print(f"Epic: {len(scan_epic())}")
    all_games.extend(scan_system())
    print(f"System: {len(scan_system())}")

    save_games(all_games)
    print(f"Всего: {len(all_games)}")

def load_from_cache():
    global all_games
    path = get_data_path("games.json")
    if not os.path.exists(path):
        return False
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        all_games = [Game.from_dict(d) for d in data]
        print(f"Из кэша: {len(all_games)}")
        return True
    except Exception as e:
        print(f"Ошибка кэша: {e}")
        return False

def assign_unassigned():
    settings = load_settings()
    changed = False
    for game in all_games:
        if game.id not in [iid for sub in settings['categories'].values() for iid in sub]:
            key = game.source.capitalize()
            if key in settings['categories']:
                settings['categories'][key].append(game.id)
                changed = True
    if changed:
        save_settings(settings)
        print("Категории обновлены")

def load_or_scan():
    if not load_from_cache():
        full_scan()
    assign_unassigned()

class Api:
    def getCategories(self):
        settings = load_settings()
        return [{"name": "Все"}] + [{"name": k} for k in settings['categories'].keys()]

    def getPrograms(self):
        settings = load_settings()
        programs = []
        for game in all_games:
            category = next((cat for cat, ids in settings['categories'].items() if game.id in ids), None)
            if not category:
                category = {'steam': 'Steam', 'epic': 'Epic', 'system': 'System', 'custom': 'Custom'}.get(game.source.lower(), 'Custom')

            if game.source.lower() == 'steam' and game.id:
                cover_url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{game.id}/header.jpg"
            elif game.cover and os.path.exists(game.cover):
                cover_url = f"file://{Path(game.cover).resolve()}"
            else:
                cover_url = ""

            programs.append({
                "name": game.name,
                "path": game.path,
                "cover": cover_url,
                "category": category,
                "source": game.source,
                "id": game.id
            })
        return programs

    def launchProgram(self, path: str, source: str = None, game_id: str = None):
        try:
            if source and source.lower() == 'steam' and game_id:
                subprocess.Popen(['start', '', f'steam://rungameid/{game_id}'], shell=True)
                return {"success": True}
            elif source and source.lower() == 'epic' and game_id:
                subprocess.Popen(['start', '', f'com.epicgames.launcher://apps/{game_id}?action=launch&silent=true'], shell=True)
                return {"success": True}
            else:
                subprocess.Popen([path], shell=True)
                return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def openFileDialog(self):
        result = webview.windows[0].create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=False,
            file_types=('Executable Files (*.exe;*.jar;*.bat)', 'All files (*.*)')
        )
        return result[0] if result else ""

    def rescan(self):
        full_scan()
        assign_unassigned()
        return {"success": True}

    def addProgram(self, name: str, path: str, category: str):
        settings = load_settings()
        if category not in settings['categories']:
            return {"success": False, "error": "Категория не существует"}

        new_id = f"custom_{int(time.time())}_{hash(name + path)}"

        new_game = Game(
            id=new_id,
            name=name,
            path=path,
            icon=None,
            source="custom",
            cover=None
        )
        global all_games
        all_games.append(new_game)
        settings['categories'][category].append(new_id)
        save_games(all_games)
        save_settings(settings)
        return {"success": True}

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
    )
    webview.start(debug=False)  # При тестировании можно True