from pathlib import Path

from ai_companion.memory import load_profile, save_profile
from ai_companion.models import UserProfile


def test_save_and_load_profile(tmp_path: Path):
    user_id = "test_user"
    profile = UserProfile(name="Alice", likes=["Python"], events=["Started project"])

    save_profile(user_id, profile, profiles_dir=tmp_path)

    loaded = load_profile(user_id, profiles_dir=tmp_path)
    assert loaded.name == "Alice"
    assert loaded.likes == ["Python"]
    assert loaded.events == ["Started project"]


def test_load_nonexistent_profile(tmp_path: Path):
    loaded = load_profile("unknown", profiles_dir=tmp_path)
    assert loaded.name is None
    assert loaded.likes == []
    assert loaded.events == []
