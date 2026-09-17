from ai_companion.models import UserProfile
from ai_companion.prompts import build_system_prompt


def test_build_system_prompt():
    profile = UserProfile(name="Bob", likes=["Pizza", "Coding"], events=["Moved to NY"])
    prompt = build_system_prompt(profile)

    assert "Name: Bob" in prompt
    assert "Likes: Pizza, Coding" in prompt
    assert "Events: Moved to NY" in prompt


def test_build_system_prompt_empty():
    profile = UserProfile()
    prompt = build_system_prompt(profile)

    assert "Name: Unknown" in prompt
    assert "Likes: None yet" in prompt
    assert "Events: None yet" in prompt
