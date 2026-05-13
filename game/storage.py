import json
from pathlib import Path

from .constants import DEFAULT_SAVE_DATA, SAVE_FILE_NAME, DEFAULT_DIFFICULTY


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SAVE_FILE = PROJECT_ROOT / SAVE_FILE_NAME


def _default_save_data():
    return DEFAULT_SAVE_DATA.copy()


def _normalize_save_data(data):
    default_data = _default_save_data()

    if not isinstance(data, dict):
        return default_data

    normalized = default_data.copy()
    normalized.update(data)

    try:
        normalized["high_score"] = max(0, int(normalized.get("high_score", 0)))
    except (TypeError, ValueError):
        normalized["high_score"] = 0

    try:
        normalized["total_money"] = max(0, int(normalized.get("total_money", 0)))
    except (TypeError, ValueError):
        normalized["total_money"] = 0

    try:
        normalized["best_stage"] = max(1, int(normalized.get("best_stage", 1)))
    except (TypeError, ValueError):
        normalized["best_stage"] = 1

    try:
        normalized["games_played"] = max(0, int(normalized.get("games_played", 0)))
    except (TypeError, ValueError):
        normalized["games_played"] = 0

    try:
        normalized["total_score"] = max(0, int(normalized.get("total_score", 0)))
    except (TypeError, ValueError):
        normalized["total_score"] = 0

    try:
        normalized["selected_skin"] = max(0, int(normalized.get("selected_skin", 0)))
    except (TypeError, ValueError):
        normalized["selected_skin"] = 0

    if normalized.get("selected_difficulty") not in {"Easy", "Medium", "Hard"}:
        normalized["selected_difficulty"] = DEFAULT_DIFFICULTY

    return normalized


def save_save_data(data):
    normalized = _normalize_save_data(data)
    SAVE_FILE.write_text(json.dumps(normalized, indent=4), encoding="utf-8")
    return normalized


def load_save_data():
    if not SAVE_FILE.exists():
        return save_save_data(_default_save_data())

    try:
        data = json.loads(SAVE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return save_save_data(_default_save_data())

    normalized = _normalize_save_data(data)

    if normalized != data:
        save_save_data(normalized)

    return normalized


def read_high_score():
    return load_save_data()["high_score"]


def write_high_score(score):
    save_data = load_save_data()
    save_data["high_score"] = max(save_data["high_score"], int(score))
    return save_save_data(save_data)["high_score"]


def update_progress(score, stage, money_earned):
    save_data = load_save_data()

    score = max(0, int(score))
    stage = max(1, int(stage))
    money_earned = max(0, int(money_earned))

    save_data["high_score"] = max(save_data["high_score"], score)
    save_data["best_stage"] = max(save_data["best_stage"], stage)
    save_data["total_money"] += money_earned
    save_data["total_score"] += score
    save_data["games_played"] += 1

    return save_save_data(save_data)


def save_player_preferences(selected_skin, selected_difficulty):
    save_data = load_save_data()
    save_data["selected_skin"] = max(0, int(selected_skin))
    
    return save_save_data(save_data)