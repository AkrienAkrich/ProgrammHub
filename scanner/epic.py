# game_launcher/scanner/epic.py  (обновлённый)

import os
import json
from utils.paths import get_epic_manifests_dir
from core.models import Game
from scanner.icons import extract_icon


def scan_epic():
    manifests_dir = get_epic_manifests_dir()
    if not manifests_dir:
        return []

    games = []
    for file in os.listdir(manifests_dir):
        if file.endswith('.item'):
            item_path = os.path.join(manifests_dir, file)
            try:
                with open(item_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                name = data.get('DisplayName')
                if not name:
                    continue
                install_location = data.get('InstallLocation')
                executable = data.get('LaunchExecutable')
                app_name = data.get('AppName')
                if install_location and executable and app_name:
                    full_path = os.path.join(install_location, executable)
                    if os.path.exists(full_path):
                        icon_path = extract_icon('epic', app_name)
                        games.append(Game(id=app_name, name=name, path=full_path, icon=icon_path, source='epic'))
            except Exception:
                continue
    return games