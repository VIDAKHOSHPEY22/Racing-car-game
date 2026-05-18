import array
import math
from pathlib import Path
import random

import pygame as pg


def load_music():
    music_folder = Path(__file__).resolve().parent.parent / "music"
    try:
        if not music_folder.exists():
            music_folder.mkdir(parents=True, exist_ok=True)
            print(f"Created '{music_folder}' folder. Please add your music files there.")
            return None

        music_files = [
            path
            for path in music_folder.iterdir()
            if path.suffix.lower() in {".mp3", ".wav", ".ogg"}
        ]

        if not music_files:
            print(f"No music files found in '{music_folder}' folder.")
            return None

        selected_music = random.choice(music_files)
        pg.mixer.music.load(str(selected_music))
        pg.mixer.music.set_volume(0.5)
        return str(selected_music)

    except Exception as e:
        print(f"Error loading music: {e}")
        return None


def create_coin_sound():
    mixer_settings = pg.mixer.get_init()
    if not mixer_settings:
        return None

    sample_rate, sample_size, channels = mixer_settings
    bit_depth = abs(sample_size)
    if bit_depth != 16:
        return None

    duration_ms = 140
    sample_count = int(sample_rate * duration_ms / 1000)
    max_amplitude = int(((2 ** (bit_depth - 1)) - 1) * 0.3)
    waveform = array.array("h")

    for index in range(sample_count):
        progress = index / sample_count
        envelope = max(0.0, 1.0 - progress)
        pitch = 880 + int(240 * progress)
        sample = int(
            math.sin((2.0 * math.pi * pitch * index) / sample_rate)
            * max_amplitude
            * envelope
        )

        for _ in range(channels):
            waveform.append(sample)

    try:
        return pg.mixer.Sound(buffer=waveform.tobytes())
    except Exception:
        return None


def create_damage_sound():
    mixer_settings = pg.mixer.get_init()
    if not mixer_settings:
        return None

    sample_rate, sample_size, channels = mixer_settings
    bit_depth = abs(sample_size)
    if bit_depth != 16:
        return None

    duration_ms = 180
    sample_count = int(sample_rate * duration_ms / 1000)
    max_amplitude = int(((2 ** (bit_depth - 1)) - 1) * 0.35)
    waveform = array.array("h")

    for index in range(sample_count):
        progress = index / sample_count
        envelope = max(0.0, 1.0 - progress)

        pitch = 170 - int(60 * progress)
        noise = random.uniform(-0.45, 0.45)
        tone = math.sin((2.0 * math.pi * pitch * index) / sample_rate)
        sample = int((tone + noise) * max_amplitude * envelope)

        for _ in range(channels):
            waveform.append(sample)

    try:
        return pg.mixer.Sound(buffer=waveform.tobytes())
    except Exception:
        return None
