"""
Tests for the core garden/streak logic.

Run with: pytest tests/test_garden_logic.py -v

These test the algorithm in isolation (no database, no API) which is
exactly why we kept it as pure functions - fast, deterministic tests
with no setup/teardown needed.
"""
from datetime import date, timedelta

from app.core.garden_logic import (
    calculate_streak,
    calculate_garden_level,
    logs_needed_for_next_level,
)

TODAY = date(2026, 8, 25)


def test_no_logs_gives_zero_streak():
    result = calculate_streak([], today=TODAY)
    assert result.current_streak == 0
    assert result.is_active is False


def test_logging_today_gives_streak_of_one():
    result = calculate_streak([TODAY], today=TODAY)
    assert result.current_streak == 1
    assert result.is_active is True


def test_consecutive_days_build_streak():
    log_dates = [TODAY - timedelta(days=i) for i in range(5)]  # today and 4 days back
    result = calculate_streak(log_dates, today=TODAY)
    assert result.current_streak == 5


def test_missed_day_within_grace_does_not_reset():
    # logged today and 2 days ago, but NOT yesterday - should still count
    # as an active streak since GRACE_DAYS=1 allows one gap
    log_dates = [TODAY, TODAY - timedelta(days=2)]
    result = calculate_streak(log_dates, today=TODAY)
    assert result.current_streak == 2
    assert result.is_active is True


def test_missed_beyond_grace_resets_streak():
    # last log was 5 days ago - well beyond the grace window
    log_dates = [TODAY - timedelta(days=5)]
    result = calculate_streak(log_dates, today=TODAY)
    assert result.current_streak == 0
    assert result.is_active is False


def test_duplicate_same_day_logs_dont_inflate_streak():
    log_dates = [TODAY, TODAY]  # logged twice in one day
    result = calculate_streak(log_dates, today=TODAY)
    assert result.current_streak == 1


def test_longest_streak_persists_after_a_break():
    # a 5-day streak two weeks ago, then a fresh 2-day streak now
    old_streak = [TODAY - timedelta(days=20 + i) for i in range(5)]
    recent_streak = [TODAY, TODAY - timedelta(days=1)]
    result = calculate_streak(old_streak + recent_streak, today=TODAY)
    assert result.current_streak == 2
    assert result.longest_streak == 5


def test_garden_level_starts_at_one():
    assert calculate_garden_level(0) == 1
    assert calculate_garden_level(1) == 2


def test_garden_level_growth_slows_down():
    # going from 0->9 logs should gain more levels than 91->100 logs
    # even though both are "9 more logs" - proves the diminishing curve
    early_gain = calculate_garden_level(9) - calculate_garden_level(0)
    later_gain = calculate_garden_level(100) - calculate_garden_level(91)
    assert early_gain > later_gain


def test_each_level_requires_more_logs_than_the_last():
    # This is the actual "diminishing returns" property we care about:
    # the gap between level thresholds grows, so later levels are
    # harder-earned than early ones (level 1->2 is easy, level 9->10
    # takes real sustained effort).
    gap_early = logs_needed_for_next_level(1)  # just hit level 2, gap to level 3
    gap_later = logs_needed_for_next_level(81)  # just hit level 10, gap to level 11
    assert gap_later > gap_early


def test_logs_needed_hits_zero_right_after_leveling_up():
    # the moment you cross a threshold, needed-for-next resets upward,
    # it should never go negative
    for total in range(0, 50):
        assert logs_needed_for_next_level(total) >= 0
