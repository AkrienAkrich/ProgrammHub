# game_launcher/scanner/system.py

import winreg
from core.registry import read_registry
from core.models import Game
from scanner.icons import extract_icon

def scan_system():
    games = []
    uninstall_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall'
    subkeys = read_registry(winreg.HKEY_LOCAL_MACHINE, uninstall_key)
    for subkey in subkeys:
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f'{uninstall_key}\\{subkey}')
            display_name = winreg.QueryValueEx(key, 'DisplayName')[0]
            install_location = winreg.QueryValueEx(key, 'InstallLocation')[0]
            if 'uninstall' not in display_name.lower() and install_location:
                # Assume executable is in install_location
                for root, dirs, files in os.walk(install_location):
                    for file in files:
                        if file.endswith('.exe') and 'uninstall' not in file.lower():
                            path = os.path.join(root, file)
                            icon_path = extract_icon('system', path)
                            games.append(Game(id=subkey, name=display_name, path=path, icon=icon_path, source='system'))
                            break
        except Exception:
            pass
    return games