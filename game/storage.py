import copy
import json
from pathlib import Path

from .constants import (
    CAR_SKINS,
    DEFAULT_DIFFICULTY,
    DEFAULT_SAVE_DATA,
    SAVE_FILE_NAME,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SAVE_FILE = PROJECT_ROOT / SAVE_FILE_NAME


def _default_save_data():
    return copy.deepcopy(DEFAULT_SAVE_DATA)


def _coerce_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _valid_skin_index(index):
    index = _coerce_int(index, 0)
    if index < 0 or index >= len(CAR_SKINS):
        return 0
    return index


def _normalize_unlocked_skins(value):
    if not isinstance(value, list):
        return [0]

    unlocked = []
    for item in value:
        try:
            index = int(item)
        except (TypeError, ValueError):
            continue

        if 0 <= index < len(CAR_SKINS) and index not in unlocked:
            unlocked.append(index)

    if 0 not in unlocked:
        unlocked.insert(0, 0)

    return unlocked or [0]


def _normalize_save_data(data):
    default_data = _default_save_data()

    if not isinstance(data, dict):
        return default_data

    normalized = default_data.copy()
    normalized.update(data)

    normalized["high_score"] = max(0, _coerce_int(normalized.get("high_score", 0), 0))
    normalized["total_money"] = max(0, _coerce_int(normalized.get("total_money", 0), 0))
    normalized["best_stage"] = max(1, _coerce_int(normalized.get("best_stage", 1), 1))
    normalized["best_distance"] = max(0, _coerce_int(normalized.get("best_distance", 0), 0))
    normalized["games_played"] = max(0, _coerce_int(normalized.get("games_played", 0), 0))
    normalized["total_score"] = max(0, _coerce_int(normalized.get("total_score", 0), 0))

    normalized["unlocked_skins"] = _normalize_unlocked_skins(
        normalized.get("unlocked_skins", [0])
    )

    normalized["selected_skin"] = _valid_skin_index(
        normalized.get("selected_skin", 0)
    )

    if normalized["selected_skin"] not in normalized["unlocked_skins"]:
        normalized["selected_skin"] = normalized["unlocked_skins"][0]

    if normalized.get("selected_difficulty") not in {"Easy", "Medium", "Hard"}:
        normalized["selected_difficulty"] = DEFAULT_DIFFICULTY

    if normalized.get("games_played", 0) == 0 and normalized.get("total_money", 0) <= 0:
        normalized["total_money"] = 100

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


def update_progress(score, stage, money_earned, distance=None):
    """Update persistent progress. Optionally pass `distance` to update best_distance.

    Backwards compatible: callers that don't pass `distance` continue to work.
    """
    save_data = load_save_data()

    score = max(0, _coerce_int(score, 0))
    stage = max(1, _coerce_int(stage, 1))
    money_earned = max(0, _coerce_int(money_earned, 0))

    save_data["high_score"] = max(save_data["high_score"], score)
    save_data["best_stage"] = max(save_data["best_stage"], stage)
    save_data["total_money"] += money_earned
    save_data["total_score"] += score
    save_data["games_played"] += 1

    if distance is not None:
        dist_val = max(0, _coerce_int(distance, 0))
        save_data["best_distance"] = max(
            save_data.get("best_distance", 0),
            dist_val,
        )

    return save_save_data(save_data)


def save_player_preferences(selected_skin, selected_difficulty):
    save_data = load_save_data()

    selected_skin = _valid_skin_index(selected_skin)
    if selected_skin in save_data.get("unlocked_skins", [0]):
        save_data["selected_skin"] = selected_skin

    if selected_difficulty in {"Easy", "Medium", "Hard"}:
        save_data["selected_difficulty"] = selected_difficulty

    return save_save_data(save_data)


def is_skin_unlocked(skin_index):
    save_data = load_save_data()
    skin_index = _valid_skin_index(skin_index)
    return skin_index in save_data.get("unlocked_skins", [0])


def buy_skin(skin_index):
    save_data = load_save_data()
    skin_index = _valid_skin_index(skin_index)

    unlocked_skins = save_data.get("unlocked_skins", [0])

    if skin_index in unlocked_skins:
        return False, "Vehicle is already unlocked."

    skin = CAR_SKINS[skin_index]
    price = max(0, _coerce_int(skin.get("price", 0), 0))

    if save_data["total_money"] < price:
        return False, "Not enough money."

    save_data["total_money"] -= price
    unlocked_skins.append(skin_index)
    save_data["unlocked_skins"] = _normalize_unlocked_skins(unlocked_skins)
    save_data["selected_skin"] = skin_index

    save_save_data(save_data)
    return True, f"{skin['name']} purchased and selected."


def select_skin(skin_index):
    save_data = load_save_data()
    skin_index = _valid_skin_index(skin_index)

    if skin_index not in save_data.get("unlocked_skins", [0]):
        return False, "This vehicle is locked."

    save_data["selected_skin"] = skin_index
    save_save_data(save_data)
    return True, f"{CAR_SKINS[skin_index]['name']} selected."



