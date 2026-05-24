import json
from pathlib import Path

from .constants import DEFAULT_SAVE_DATA, SAVE_FILE_NAME, DEFAULT_DIFFICULTY, MAX_SANE_TOTAL_MONEY


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

    # Clamp saved money to a reasonable upper bound to avoid runaway values
    # caused by legacy bugs or corrupted save files.
    try:
        normalized["total_money"] = min(normalized["total_money"], int(MAX_SANE_TOTAL_MONEY))
    except Exception:
        pass

    try:
        normalized["last_successful_total_money"] = max(0, int(normalized.get("last_successful_total_money", normalized["total_money"])))
    except (TypeError, ValueError):
        normalized["last_successful_total_money"] = normalized["total_money"]

    # Ensure last successful money is also within sane bounds
    try:
        normalized["last_successful_total_money"] = min(normalized["last_successful_total_money"], int(MAX_SANE_TOTAL_MONEY))
    except Exception:
        pass

    try:
        normalized["best_stage"] = max(1, int(normalized.get("best_stage", 1)))
    except (TypeError, ValueError):
        normalized["best_stage"] = 1

    try:
        normalized["best_distance"] = max(0, int(normalized.get("best_distance", 0)))
    except (TypeError, ValueError):
        normalized["best_distance"] = 0

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

    if normalized.get("games_played", 0) == 0 and normalized.get("total_money", 0) <= 0:
        normalized["total_money"] = 100
        normalized["last_successful_total_money"] = 100

    if normalized.get("last_successful_total_money", 0) <= 0:
        normalized["last_successful_total_money"] = normalized.get("total_money", 100)

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


def update_progress(score, stage, money_earned=0, distance=None, persist_money=True):
    """Update persistent progress. Optionally pass distance to update best_distance.

    Backwards compatible: callers that don't pass distance continue to work.
    """
    def _coerce_int(v, default=0):
        try:
            return int(v)
        except (TypeError, ValueError):
            return default

    save_data = load_save_data()

    score = max(0, _coerce_int(score, 0))
    stage = max(1, _coerce_int(stage, 1))
    money_earned = _coerce_int(money_earned, 0)

    save_data["high_score"] = max(save_data["high_score"], score)
    save_data["best_stage"] = max(save_data["best_stage"], stage)
    if persist_money:
        save_data["total_money"] = max(0, save_data["total_money"] + money_earned)
    save_data["total_score"] += score
    save_data["games_played"] += 1

    if distance is not None:
        try:
            dist_val = max(0, int(distance))
            save_data["best_distance"] = max(save_data.get("best_distance", 0), dist_val)
        except (TypeError, ValueError):
            pass

    return save_save_data(save_data)


def store_successful_money(total_money):
    save_data = load_save_data()
    try:
        money_value = max(0, int(total_money))
    except (TypeError, ValueError):
        money_value = max(0, int(save_data.get("total_money", 100)))

    save_data["total_money"] = money_value
    save_data["last_successful_total_money"] = money_value
    return save_save_data(save_data)


def restore_last_successful_money():
    save_data = load_save_data()
    restored_money = max(0, int(save_data.get("last_successful_total_money", save_data.get("total_money", 100))))
    save_data["total_money"] = restored_money
    save_data["last_successful_total_money"] = restored_money
    return save_save_data(save_data)


def save_player_preferences(selected_skin, selected_difficulty):
    save_data = load_save_data()
    save_data["selected_skin"] = max(0, int(selected_skin))
    if selected_difficulty in {"Easy", "Medium", "Hard"}:
        save_data["selected_difficulty"] = selected_difficulty

    return save_save_data(save_data)
