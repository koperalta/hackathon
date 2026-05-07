from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from math import ceil
from typing import Deque, Dict


@dataclass
class PitxWaitPrediction:
    people_count: int
    estimated_wait_minutes: int
    service_level: str


class PitxWaitTimeForecaster:
    """
    Demo-optimized wait-time forecaster for PITX using only live people counts.

    Why this approach:
      - deterministic + explainable for judges
      - no heavy ML deps (sklearn/torch) beyond YOLO itself
      - stable output via smoothing (prevents "jittery" demo UI)
    """

    def __init__(self) -> None:
        self._recent_counts: Deque[int] = deque(maxlen=12)

        # PITX queue assumptions (tune these for your demo video):
        self.bus_capacity = 45            # average bus capacity per dispatch
        self.dispatch_headway_min = 6     # average minutes between bus dispatch
        self.boarding_rate_per_min = 9    # boarding throughput at gate (pax/min)
        self.base_overhead_min = 3        # ticketing / walking / gate friction

    def _smoothed_count(self, current: int) -> int:
        self._recent_counts.append(int(current))
        # Simple trimmed mean-ish smoothing: average the last N
        values = list(self._recent_counts)
        if not values:
            return current
        values.sort()
        if len(values) >= 6:
            values = values[1:-1]  # trim extremes
        return int(round(sum(values) / len(values)))

    def _service_level(self, wait_minutes: int) -> str:
        if wait_minutes >= 25:
            return "Heavy"
        if wait_minutes >= 16:
            return "Moderate"
        return "Light"

    def predict(self, current_people_count: int) -> PitxWaitPrediction:
        people = max(0, int(current_people_count))
        smoothed = self._smoothed_count(people)

        # 1) Dispatch cycles needed to clear the current queue
        cycles = max(1, ceil(smoothed / max(self.bus_capacity, 1)))
        dispatch_wait = (cycles - 1) * self.dispatch_headway_min

        # 2) Boarding time for the queue currently visible (bounded by headway)
        boarding_time = min(
            self.dispatch_headway_min,
            int(round(smoothed / max(self.boarding_rate_per_min, 1))),
        )

        # 3) Total wait estimate
        wait_minutes = self.base_overhead_min + dispatch_wait + boarding_time
        wait_minutes = max(4, min(60, int(wait_minutes)))

        return PitxWaitPrediction(
            people_count=people,
            estimated_wait_minutes=wait_minutes,
            service_level=self._service_level(wait_minutes),
        )

    def as_dict(self, current_people_count: int) -> Dict[str, object]:
        pred = self.predict(current_people_count)
        return {
            "people_count": pred.people_count,
            "estimated_wait_minutes": pred.estimated_wait_minutes,
            "service_level": pred.service_level,
        }


pitx_forecaster = PitxWaitTimeForecaster()

