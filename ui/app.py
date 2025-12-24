# game_launcher/ui/app.py

import customtkinter as ctk
from PIL import Image
import os
from tkinter import filedialog, messagebox
from core.launcher import start_game
from scanner.icons import extract_icon
from core.models import Game
from core.storage import save_games, save_settings

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self, games, settings):
        super().__init__()
        self.title("Akrien Launcher")
        self.geometry("1280x720")
        self.minsize(1000, 600)

        # Удаляем дубликаты
        seen = set()
        unique_games = []
        for g in games:
            key = (g.id, g.source)
            if key not in seen:
                seen.add(key)
                unique_games.append(g)
        self.games = unique_games
        self.settings = settings
        self.selected_game = None
        self.current_category = None

        self.setup_ui()
        self.show_all_games()  # По умолчанию показываем все игры

    def setup_ui(self):
        # Верхняя панель
        top_frame = ctk.CTkFrame(self, height=60)
        top_frame.pack(fill="x", padx=10, pady=10)

        self.search_entry = ctk.CTkEntry(top_frame, placeholder_text="Поиск игр...", width=400)
        self.search_entry.pack(side="left", padx=10)
        self.search_entry.bind("<KeyRelease>", self.filter_games)

        ctk.CTkButton(top_frame, text="Добавить программу", command=self.add_custom_game).pack(side="left", padx=10)
        ctk.CTkButton(top_frame, text="Новая категория", command=self.create_category).pack(side="left", padx=10)

        # Левый фрейм
        self.left_frame = ctk.CTkFrame(self, width=350, corner_radius=0)
        self.left_frame.pack(side="left", fill="y")
        self.left_frame.pack_propagate(False)

        ctk.CTkLabel(self.left_frame, text="Категории", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 10))

        self.categories_scroll = ctk.CTkScrollableFrame(self.left_frame, height=200)
        self.categories_scroll.pack(fill="x", padx=15)

        ctk.CTkLabel(self.left_frame, text="Игры", font=ctk.CTkFont(size=16)).pack(anchor="w", padx=20, pady=(10, 5))
        self.games_scroll = ctk.CTkScrollableFrame(self.left_frame)
        self.games_scroll.pack(fill="both", expand=True, padx=15, pady=5)

        self.load_categories()

        # Правый фрейм
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.pack(side="right", fill="both", expand=True)

        self.no_game_label = ctk.CTkLabel(self.right_frame, text="Выберите игру", font=ctk.CTkFont(size=28), text_color="gray60")
        self.no_game_label.pack(expand=True)

    def load_categories(self):
        for widget in self.categories_scroll.winfo_children():
            widget.destroy()

        for cat_name in self.settings["categories"]:
            cat_frame = ctk.CTkFrame(self.categories_scroll)
            cat_frame.pack(fill="x", pady=3, padx=5)

            cat_btn = ctk.CTkButton(
                cat_frame,
                text=cat_name,
                anchor="w",
                fg_color="transparent",
                hover_color=("#3a3a3a", "#2f2f2f"),
                command=lambda c=cat_name: self.show_category(c)
            )
            cat_btn.pack(side="left", fill="x", expand=True)

            # Кнопка удаления
            delete_btn = ctk.CTkButton(
                cat_frame,
                text="×",
                width=30,
                fg_color="transparent",
                hover_color="red",
                command=lambda c=cat_name: self.delete_category(c)
            )
            delete_btn.pack(side="right")

    def show_category(self, category):
        self.current_category = category
        self.filter_games()

    def show_all_games(self):
        self.current_category = None
        self.filter_games()

    def filter_games(self, event=None):
        # Очищаем список игр
        for widget in self.games_scroll.winfo_children():
            widget.destroy()

        search = self.search_entry.get().lower()
        displayed_games = self.games

        # Фильтр по категории
        if self.current_category:
            cat_ids = self.settings["categories"].get(self.current_category, [])
            displayed_games = [g for g in displayed_games if str(g.id) in [str(i) for i in cat_ids]]

        # Фильтр по поиску
        if search:
            displayed_games = [g for g in displayed_games if search in g.name.lower()]

        for game in displayed_games:
            btn = ctk.CTkButton(
                self.games_scroll,
                text=game.name,
                anchor="w",
                height=40,
                fg_color="transparent",
                hover_color=("#3a3a3a", "#2f2f2f"),
                command=lambda g=game: self.select_game(g)
            )

            if game.icon and os.path.exists(game.icon):
                try:
                    img = Image.open(game.icon).resize((32, 32), Image.LANCZOS)
                    img_ctk = ctk.CTkImage(light_image=img, dark_image=img, size=(32, 32))
                    btn.configure(image=img_ctk, compound="left")
                except:
                    pass

            btn.pack(fill="x", pady=1, padx=5)

    def select_game(self, game):
        self.selected_game = game
        for w in self.right_frame.winfo_children():
            w.destroy()

        cover_to_use = game.cover or game.icon
        if cover_to_use and os.path.exists(cover_to_use):
            try:
                cover_img = Image.open(cover_to_use)
                ratio = cover_img.width / cover_img.height
                if ratio > 2:
                    new_size = (960, 360)
                else:
                    new_size = (600, 400)
                cover_img = cover_img.resize(new_size, Image.LANCZOS)
                cover_ctk = ctk.CTkImage(light_image=cover_img, dark_image=cover_img, size=new_size)
                ctk.CTkLabel(self.right_frame, image=cover_ctk, text="").pack(pady=(30, 10))
            except:
                pass

        ctk.CTkLabel(self.right_frame, text=game.name, font=ctk.CTkFont(size=36, weight="bold")).pack(pady=(0, 20))

        info = f"Источник: {game.source.upper()}"
        if game.total_minutes > 0:
            hours = int(game.total_minutes // 60)
            mins = int(game.total_minutes % 60)
            info += f"\nВремя в игре: {hours} ч. {mins} мин."

        ctk.CTkLabel(self.right_frame, text=info, font=ctk.CTkFont(size=16), justify="left").pack(anchor="w", padx=80)

        ctk.CTkButton(
            self.right_frame,
            text="PLAY",
            font=ctk.CTkFont(size=32, weight="bold"),
            width=400, height=80,
            fg_color="#1a7f37", hover_color="#148c30",
            command=lambda: start_game(game)
        ).pack(pady=40)

    def create_category(self):
        dialog = ctk.CTkInputDialog(text="Название категории:", title="Новая категория")
        name = dialog.get_input()
        if name and name not in self.settings["categories"]:
            self.settings["categories"][name] = []
            save_settings(self.settings)
            self.load_categories()

    def delete_category(self, cat_name):
        if cat_name in ["Steam", "Epic", "System", "Custom"]:
            messagebox.showwarning("Ошибка", "Базовые категории нельзя удалить")
            return
        if messagebox.askyesno("Удалить категорию", f"Удалить '{cat_name}'?"):
            del self.settings["categories"][cat_name]
            save_settings(self.settings)
            self.load_categories()
            if self.current_category == cat_name:
                self.show_all_games()

    def add_custom_game(self):
        exe_path = filedialog.askopenfilename(filetypes=[("Программы", "*.exe *.jar *.bat")])
        if not exe_path:
            return

        name = os.path.basename(exe_path).rsplit('.', 1)[0]
        icon_path = extract_icon("custom", exe_path)
        game_id = f"custom_{os.urandom(4).hex()}"

        new_game = Game(id=game_id, name=name, path=exe_path, icon=icon_path, source="custom")
        self.games.append(new_game)
        save_games(self.games)

        if "Custom" not in self.settings["categories"]:
            self.settings["categories"]["Custom"] = []
        self.settings["categories"]["Custom"].append(game_id)
        save_settings(self.settings)

        self.filter_games()