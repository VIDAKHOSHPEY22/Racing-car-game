from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
HIGH_SCORE_FILE = PROJECT_ROOT / "highscore.txt"


def ensure_storage_files():
    HIGH_SCORE_FILE.touch(exist_ok=True)
    if not HIGH_SCORE_FILE.read_text(encoding="utf-8").strip():
        HIGH_SCORE_FILE.write_text("0", encoding="utf-8")


def read_high_score():
    ensure_storage_files()
    try:
        return int(HIGH_SCORE_FILE.read_text(encoding="utf-8").strip())
    except ValueError:
        HIGH_SCORE_FILE.write_text("0", encoding="utf-8")
        return 0


def write_high_score(score):
    ensure_storage_files()
    best_score = max(score, read_high_score())
    HIGH_SCORE_FILE.write_text(str(best_score), encoding="utf-8")
    return best_score
