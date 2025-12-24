# game_launcher/core/models.py

import time


class Game:
    def __init__(self, id, name, path, icon, source, last_played=None, total_minutes=0, cover=None):
        self.id = id
        self.name = name
        self.path = path
        self.icon = icon
        self.source = source
        self.last_played = last_played or time.time()
        self.total_minutes = total_minutes
        self.cover = cover  # Новый путь к большой обложке

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'path': self.path,
            'icon': self.icon,
            'source': self.source,
            'last_played': self.last_played,
            'total_minutes': self.total_minutes,
            'cover': self.cover
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data['id'],
            name=data['name'],
            path=data['path'],
            icon=data['icon'],
            source=data['source'],
            last_played=data.get('last_played'),
            total_minutes=data.get('total_minutes', 0),
            cover=data.get('cover')
        )