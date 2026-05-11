import os
import random

import pygame as pg


def load_music():
    music_folder = "music"
    try:
        if not os.path.exists(music_folder):
            os.makedirs(music_folder)
            print(f"Created '{music_folder}' folder. Please add your music files there.")
            return None
        music_files = [f for f in os.listdir(music_folder) if f.endswith((".mp3", ".wav", ".ogg"))]
        if not music_files:
            print(f"No music files found in '{music_folder}' folder.")
            return None
        selected_music = os.path.join(music_folder, random.choice(music_files))
        pg.mixer.music.load(selected_music)
        pg.mixer.music.set_volume(0.5)
        return selected_music
    except Exception as e:
        print(f"Error loading music: {e}")
        return None
