# game_launcher/utilits/paths.py  (обновлённый файл)

import os
import winreg

def get_data_path(file_name=''):
    base = os.path.join(os.getenv('APPDATA'), 'GameLauncher')
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, file_name) if file_name else base

def get_settings_path():
    return get_data_path('settings.json')

def get_icons_path():
    icons_dir = get_data_path('icons')
    os.makedirs(icons_dir, exist_ok=True)
    return icons_dir

def get_steam_path():
    """Автоопределение пути к Steam через реестр"""
    keys_to_try = [
        (winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\WOW6432Node\Valve\Steam'),
        (winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Valve\Steam'),
        (winreg.HKEY_CURRENT_USER, r'Software\Valve\Steam'),
    ]
    for hive, key_path in keys_to_try:
        try:
            key = winreg.OpenKey(hive, key_path)
            path, _ = winreg.QueryValueEx(key, 'InstallPath')
            winreg.CloseKey(key)
            if os.path.exists(path):
                return path
        except Exception:
            pass
    return None

def get_epic_manifests_dir():
    """Автоопределение папки с манифестами Epic Games"""
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\WOW6432Node\Epic Games\EpicGamesLauncher')
        app_data_path, _ = winreg.QueryValueEx(key, 'AppDataPath')
        winreg.CloseKey(key)
        manifests_dir = os.path.join(app_data_path, 'Manifests')
        if os.path.exists(manifests_dir):
            return manifests_dir
    except Exception:
        pass
    # Резервный вариант: стандартная папка
    default = r'C:\ProgramData\Epic\EpicGamesLauncher\Data\Manifests'
    if os.path.exists(default):
        return default
    return None