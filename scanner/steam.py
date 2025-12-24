# game_launcher/scanner/steam.py

import os
import re
import requests
from utils.paths import get_steam_path, get_icons_path
from core.models import Game
from scanner.icons import extract_icon


def download_cover(appid):
    cover_dir = get_icons_path()
    os.makedirs(cover_dir, exist_ok=True)
    cover_path = os.path.join(cover_dir, f"cover_{appid}.jpg")

    if os.path.exists(cover_path):
        return cover_path

    url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/header.jpg"
    try:
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            with open(cover_path, "wb") as f:
                f.write(r.content)
            return cover_path
    except:
        pass
    return None


def parse_libraryfolders(vdf_path):
    if not os.path.exists(vdf_path):
        return []
    libraries = []
    try:
        with open(vdf_path, "r", encoding="utf-8") as f:
            content = f.read()
        matches = re.findall(r'"path"\s+"([^"]+)"', content)
        libraries.extend(matches)
    except:
        pass
    return libraries


def scan_steam():
    steam_path = get_steam_path()
    if not steam_path:
        return []

    vdf_path = os.path.join(steam_path, "steamapps", "libraryfolders.vdf")
    libraries = parse_libraryfolders(vdf_path)
    libraries.append(steam_path)  # Основная библиотека всегда

    games = []
    for lib in libraries:
        steamapps = os.path.join(lib, "steamapps")
        if not os.path.exists(steamapps):
            continue
        for file in os.listdir(steamapps):
            if file.startswith("appmanifest_") and file.endswith(".acf"):
                manifest_path = os.path.join(steamapps, file)
                try:
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    appid_match = re.search(r'"appid"\s+"(\d+)"', content)
                    name_match = re.search(r'"name"\s+"([^"]+)"', content)
                    installdir_match = re.search(r'"installdir"\s+"([^"]+)"', content)
                    if not all([appid_match, name_match, installdir_match]):
                        continue
                    appid = appid_match.group(1)
                    name = name_match.group(1)
                    installdir = installdir_match.group(1)

                    game_folder = os.path.join(steamapps, "common", installdir)
                    if not os.path.exists(game_folder):
                        continue

                    # Поиск исполняемого файла: .exe или .jar (для Java игр как BrainOut)
                    exe_path = None
                    for root, _, files in os.walk(game_folder):
                        for f in files:
                            basename = f.lower()
                            if basename.endswith('.exe') and "uninstall" not in basename and "redist" not in basename:
                                exe_path = os.path.join(root, f)
                                break
                            elif basename.endswith('.jar'):
                                exe_path = os.path.join(root, f)  # Для Java — путь к .jar
                                break
                        if exe_path:
                            break

                    # Если не нашли exe/jar — пропускаем
                    if not exe_path:
                        continue

                    icon_path = extract_icon("steam", appid)
                    cover_path = download_cover(appid)

                    games.append(Game(
                        id=appid,
                        name=name,
                        path=exe_path,
                        icon=icon_path,
                        source="steam",
                        cover=cover_path
                    ))
                except Exception:
                    continue
    return games