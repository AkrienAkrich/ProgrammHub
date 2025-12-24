# game_launcher/scanner/icons.py

import os
from utils.paths import get_icons_path
import win32gui
import win32ui
from PIL import Image


def extract_icon(source, identifier):
    icons_dir = get_icons_path()
    os.makedirs(icons_dir, exist_ok=True)
    icon_path = os.path.join(icons_dir, f'{source}_{identifier}.ico')

    if os.path.exists(icon_path):
        return icon_path

    if source == 'steam':
        # Placeholder for Steam icon extraction
        # In reality, use Steam's icon cache
        pass
    elif source == 'epic':
        # Placeholder for Epic icon
        pass
    elif source == 'system':
        # Extract from .exe
        large, small = win32gui.ExtractIconEx(identifier, 0)
        if large:
            hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
            hbmp = win32ui.CreateBitmap()
            hbmp.CreateCompatibleBitmap(hdc, 32, 32)
            hdc = hdc.CreateCompatibleDC()
            hdc.SelectObject(hbmp)
            hdc.DrawIcon((0, 0), large[0])
            bmpinfo = hbmp.GetInfo()
            bmpstr = hbmp.GetBitmapBits(True)
            img = Image.frombuffer('RGBA', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRA', 0, 1)
            img.save(icon_path)
            win32gui.DestroyIcon(large[0])
            return icon_path

    # Default icon if extraction fails
    return 'default.ico'