import pytest
from freezegun import freeze_time


@pytest.mark.skip("Used for debugging delta date issue")
def test_freezer(settings):
    """
    Try to understand humanizer 'rounding' behaviors, related to issue #12.

    Disabled for now until test failures comes back.
    """
    import datetime
    import humanize

    # last_entry = datetime.datetime.fromisoformat("2024-07-01T09:48:43")
    resolved_published = datetime.datetime.fromisoformat("2023-04-01T09:31:37")

    with freeze_time("2024-07-30 10:00:00"):
        now = datetime.datetime.now()
        delta = now - resolved_published
        resolved_age = humanize.naturaldelta(delta)
        print("For now:", now)
        print("   - delta:", delta)
        print("   - resolved_age:", resolved_age)

    with freeze_time("2024-07-25 10:00:00"):
        now = datetime.datetime.now()
        delta = now - resolved_published
        resolved_age = humanize.naturaldelta(delta)
        print("For now:", now)
        print("   - delta:", delta)
        print("   - resolved_age:", resolved_age)

    with freeze_time("2024-07-20 10:00:00"):
        now = datetime.datetime.now()
        delta = now - resolved_published
        resolved_age = humanize.naturaldelta(delta)
        print("For now:", now)
        print("   - delta:", delta)
        print("   - resolved_age:", resolved_age)

    with freeze_time("2024-07-10 10:00:00"):
        now = datetime.datetime.now()
        delta = now - resolved_published
        resolved_age = humanize.naturaldelta(delta)
        print("For now:", now)
        print("   - delta:", delta)
        print("   - resolved_age:", resolved_age)

    assert 1 == 42
