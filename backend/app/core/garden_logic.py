"""
Core garden/streak logic.

This is deliberately kept separate from the API routes (no FastAPI or
DB session imports here) so it's pure, easily unit-testable business
logic. The API layer just calls into this.

Design decisions worth knowing (and being able to explain):

1. Streaks are calculated from log dates, not a stored counter that's
   incremented on each request. Recomputing from source-of-truth dates
   avoids the counter ever drifting out of sync with reality (e.g. if
   a log gets deleted, a naive counter would need manual correction;
   this version self-corrects automatically).

2. A single missed day doesn't zero the streak instantly - it enters
   a "grace" state for GRACE_DAYS before resetting. This mirrors how
   apps like Duolingo handle streaks and avoids punishing someone for
   one bad day, which is a real product decision, not just a technical
   one.

3. Garden level is a monotonically increasing function of total
   logs, but growth rate slows down at higher levels (diminishing
   returns), so early progress feels fast and rewarding, while long-
   term growth still means something instead of the garden "maxing
   out" too quickly.
"""
import math
from dataclasses import dataclass
from datetime import date, timedelta

GRACE_DAYS = 1  # how many missed days before a streak resets to 0


@dataclass
class StreakResult:
    current_streak: int
    longest_streak: int
    is_active: bool  # False if the streak just reset


def calculate_streak(log_dates: list[date], today: date | None = None) -> StreakResult:
    """
    Given all the dates a habit was logged, compute the current streak.

    log_dates: list of dates the user logged this habit (may be
               unsorted, may contain duplicates from same-day double logs)
    today: injected for testability rather than calling date.today()
           directly inside the function
    """
    if today is None:
        today = date.today()

    if not log_dates:
        return StreakResult(current_streak=0, longest_streak=0, is_active=False)

    unique_dates = sorted(set(log_dates))

    # Walk backwards from today to find the current streak, allowing
    # gaps of up to GRACE_DAYS before we consider it broken.
    current_streak = 0
    cursor = today
    date_set = set(unique_dates)

    while True:
        if cursor in date_set:
            current_streak += 1
            cursor -= timedelta(days=1)
        else:
            # check if we're still within the grace window from `cursor`
            gap_start = cursor
            found_within_grace = False
            for grace_offset in range(1, GRACE_DAYS + 1):
                if (gap_start - timedelta(days=grace_offset)) in date_set:
                    found_within_grace = True
                    cursor = gap_start - timedelta(days=grace_offset)
                    break
            if not found_within_grace:
                break

    # Longest streak ever: scan all dates for the longest consecutive run
    longest_streak = 0
    run = 0
    prev = None
    for d in unique_dates:
        if prev is not None and (d - prev).days <= GRACE_DAYS + 1:
            run += 1
        else:
            run = 1
        longest_streak = max(longest_streak, run)
        prev = d

    is_active = (today in date_set) or ((today - timedelta(days=1)) in date_set)

    return StreakResult(
        current_streak=current_streak,
        longest_streak=max(longest_streak, current_streak),
        is_active=is_active,
    )


def calculate_garden_level(total_logs: int) -> int:
    """
    Diminishing-returns growth curve: level increases with total logs,
    but each subsequent level requires more logs than the last.

    Using a square-root curve so early levels come quickly (rewarding
    for a brand new user) while later levels require sustained,
    long-term consistency rather than a single burst of activity.
    """
    if total_logs <= 0:
        return 1
    return max(1, math.floor(math.sqrt(total_logs)) + 1)


def logs_needed_for_next_level(total_logs: int) -> int:
    """How many more logs until the garden levels up again (for UI progress bars)."""
    current_level = calculate_garden_level(total_logs)
    # inverse of calculate_garden_level: find smallest total_logs that produces current_level + 1
    next_level = current_level + 1
    logs_required = (next_level - 1) ** 2
    return max(0, logs_required - total_logs)
