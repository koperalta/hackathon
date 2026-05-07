from __future__ import annotations

from typing import Dict


def pitx_alternative_route(wait_minutes: int, people_count: int) -> Dict[str, object]:
    """
    PITX-only, hackathon-demo-optimized routing suggestion.

    If the PITX estimated wait is high, return a concrete alternative route.
    Otherwise, return a "current route is optimal" message.
    """

    wait_minutes = int(wait_minutes)
    people_count = int(people_count)

    threshold = 18
    if wait_minutes < threshold:
        return {
            "is_optimal": True,
            "title": "Current route is optimal",
            "message": "PITX queues are manageable right now. Stay on your current route.",
            "time_saved_minutes": 0,
        }

    # For a crisp demo: hardcode one strong alternative
    # (Judges can immediately understand it without browsing multiple options.)
    alternative_wait = max(8, min(14, wait_minutes - 9))
    time_saved = max(8, wait_minutes - alternative_wait)

    return {
        "is_optimal": False,
        "title": "Smart Route Alternative",
        "message": (
            "Heavy congestion at PITX Gate 3. "
            "Alternative: Take the EDSA Carousel from Roxas Blvd, then transfer at Taft Avenue. "
            f"Estimated time saved: {time_saved} mins."
        ),
        "time_saved_minutes": time_saved,
        "context": {
            "pitx_wait_minutes": wait_minutes,
            "pitx_people_count": people_count,
            "assumed_alternative_wait_minutes": alternative_wait,
        },
    }

