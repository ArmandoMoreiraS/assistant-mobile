import json
from pathlib import Path

from .models import Turn, UserProfile

DEFAULT_PROFILES_DIR = Path("data/profiles")


def get_profile_path(user_id: str, profiles_dir: Path = DEFAULT_PROFILES_DIR) -> Path:
    return profiles_dir / f"{user_id}.json"


def load_profile(user_id: str, profiles_dir: Path = DEFAULT_PROFILES_DIR) -> UserProfile:
    path = get_profile_path(user_id, profiles_dir)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return UserProfile(**data)
    return UserProfile()


def save_profile(
    user_id: str, profile: UserProfile, profiles_dir: Path = DEFAULT_PROFILES_DIR
) -> None:
    profiles_dir.mkdir(parents=True, exist_ok=True)
    path = get_profile_path(user_id, profiles_dir)
    with open(path, "w", encoding="utf-8") as f:
        f.write(profile.model_dump_json(indent=2))


def get_history_path(user_id: str, profiles_dir: Path = DEFAULT_PROFILES_DIR) -> Path:
    return profiles_dir / f"{user_id}_history.json"


def load_history(user_id: str, profiles_dir: Path = DEFAULT_PROFILES_DIR) -> list[Turn]:
    path = get_history_path(user_id, profiles_dir)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [Turn(**t) for t in data]
    return []


def save_history(
    user_id: str, history: list[Turn], profiles_dir: Path = DEFAULT_PROFILES_DIR
) -> None:
    profiles_dir.mkdir(parents=True, exist_ok=True)
    path = get_history_path(user_id, profiles_dir)
    with open(path, "w", encoding="utf-8") as f:
        json.dump([t.model_dump() for t in history], f, indent=2, ensure_ascii=False)
