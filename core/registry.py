# game_launcher/core/registry.py

import winreg

def read_registry(hive, key):
    try:
        reg_key = winreg.OpenKey(hive, key)
        subkeys = []
        i = 0
        while True:
            try:
                subkey = winreg.EnumKey(reg_key, i)
                subkeys.append(subkey)
                i += 1
            except OSError:
                break
        winreg.CloseKey(reg_key)
        return subkeys
    except Exception:
        return []