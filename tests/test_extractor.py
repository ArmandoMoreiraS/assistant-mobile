from ai_companion.extractor import ExtractedInfo, update_profile_from_extraction
from ai_companion.models import UserProfile


def test_update_profile_from_extraction():
    profile = UserProfile(name="Alice", likes=["Reading"], events=[])
    extracted = ExtractedInfo(
        name="Alice", new_likes=["Writing"], new_events=["Started a new book"]
    )

    updated = update_profile_from_extraction(profile, extracted)

    assert updated.name == "Alice"
    assert "Writing" in updated.likes
    assert "Reading" in updated.likes
    assert "Started a new book" in updated.events
