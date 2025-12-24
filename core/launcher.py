# game_launcher/core/launcher.py

import subprocess


def start_game(game, discord_rpc=True):
    try:
        if game.source == 'steam':
            # Запуск через Steam URI — надёжно, запускает игру правильно
            subprocess.Popen(['start', f'steam://rungameid/{game.id}'], shell=True)
        elif game.source == 'epic':
            # Для Epic — через URI (если id — это AppName)
            subprocess.Popen(['start', f'epic://launch/{game.id}'], shell=True)
        else:
            # Для system и других — прямой запуск exe
            subprocess.Popen([game.path], shell=True)
    except Exception as e:
        print("Ошибка запуска игры:", e)