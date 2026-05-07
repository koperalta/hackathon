from __future__ import annotations

from datetime import datetime
import random
import threading
from typing import Dict, List, Optional

import cv2
import numpy as np


class PeopleCounter:
    def __init__(self) -> None:
        self.camera_index = 0
        self.capture: Optional[cv2.VideoCapture] = None
        self.lock = threading.Lock()
        self.simulated_count = 8
        self.entry_count = 0
        self.exit_count = 0
        self.passby_count = 0
        self.next_track_id = 1
        self.tracks: Dict[int, Dict[str, object]] = {}
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=350, varThreshold=42, detectShadows=True)
        self.last_result: Dict[str, object] = {
            "count": 8,
            "capacity": 20,
            "occupancy_percent": 40,
            "occupancy_level": "Maluwag",
            "confidence": 74,
            "source": "simulated",
            "timestamp": datetime.utcnow().isoformat(),
            "tracking": {
                "camera_active": False,
                "visible_now": 8,
                "entered": 0,
                "exited": 0,
                "passed_by": 0,
                "tracking_mode": "simulation",
                "line_position": 240,
                "active_tracks": 0,
            },
        }

    def _level_from_percent(self, percent: int) -> str:
        if percent < 50:
            return "Maluwag"
        if percent <= 80:
            return "Medyo puno"
        if percent >= 90:
            return "Siksikan"
        return "Pa-puno"

    def _safe_open_camera(self) -> bool:
        if self.capture and self.capture.isOpened():
            return True
        self.capture = cv2.VideoCapture(self.camera_index)
        if not self.capture or not self.capture.isOpened():
            self.capture = None
            return False
        ok, _ = self.capture.read()
        if not ok:
            self.capture.release()
            self.capture = None
            return False
        return True

    def _release_camera(self) -> None:
        if self.capture and self.capture.isOpened():
            self.capture.release()
        self.capture = None

    def reset_tracking(self) -> Dict[str, object]:
        with self.lock:
            self.entry_count = 0
            self.exit_count = 0
            self.passby_count = 0
            self.next_track_id = 1
            self.tracks = {}
            if "tracking" in self.last_result:
                self.last_result["tracking"]["entered"] = 0
                self.last_result["tracking"]["exited"] = 0
                self.last_result["tracking"]["passed_by"] = 0
                self.last_result["tracking"]["active_tracks"] = 0
        return self.last_result

    def _simulate_status(self, capacity: int) -> Dict[str, object]:
        fluctuation = random.choice([-2, -1, 0, 1, 2, 3])
        self.simulated_count = max(0, min(capacity, self.simulated_count + fluctuation))
        occupancy_percent = int((self.simulated_count / max(capacity, 1)) * 100)
        entered = max(0, self.entry_count + random.choice([0, 0, 1]))
        passed_by = max(entered, self.passby_count + random.choice([0, 1, 1, 2]))
        tracking = {
            "camera_active": False,
            "visible_now": self.simulated_count,
            "entered": entered,
            "exited": self.exit_count,
            "passed_by": passed_by,
            "tracking_mode": "simulation fallback",
            "line_position": 240,
            "active_tracks": self.simulated_count,
        }
        self.entry_count = entered
        self.passby_count = passed_by
        result = {
            "count": self.simulated_count,
            "capacity": capacity,
            "occupancy_percent": occupancy_percent,
            "occupancy_level": self._level_from_percent(occupancy_percent),
            "confidence": random.randint(62, 79),
            "source": "simulated",
            "timestamp": datetime.utcnow().isoformat(),
            "tracking": tracking,
        }
        self.last_result = result
        return result

    def _extract_moving_people(self, frame: np.ndarray) -> List[Dict[str, object]]:
        resized = cv2.resize(frame, (640, 480))
        fg_mask = self.bg_subtractor.apply(resized)
        _, thresh = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        opened = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
        dilated = cv2.dilate(opened, kernel, iterations=3)
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detections: List[Dict[str, object]] = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 1200:
                continue
            x, y, w, h = cv2.boundingRect(contour)
            if h < 60 or w < 20:
                continue
            centroid = (x + (w // 2), y + (h // 2))
            detections.append({"bbox": (x, y, w, h), "centroid": centroid, "area": area})
        return detections

    def _match_tracks(self, detections: List[Dict[str, object]], line_y: int) -> None:
        updated_track_ids = set()

        for detection in detections:
            centroid_x, centroid_y = detection["centroid"]
            matched_id = None
            min_distance = 80

            for track_id, track in self.tracks.items():
                prev_x, prev_y = track["centroid"]
                distance = ((centroid_x - prev_x) ** 2 + (centroid_y - prev_y) ** 2) ** 0.5
                if distance < min_distance:
                    min_distance = distance
                    matched_id = track_id

            if matched_id is None:
                matched_id = self.next_track_id
                self.next_track_id += 1
                self.tracks[matched_id] = {
                    "centroid": detection["centroid"],
                    "previous_centroid": detection["centroid"],
                    "bbox": detection["bbox"],
                    "last_seen": datetime.utcnow(),
                    "counted_entry": False,
                    "counted_exit": False,
                    "counted_passby": False,
                }
            else:
                self.tracks[matched_id]["previous_centroid"] = self.tracks[matched_id]["centroid"]
                self.tracks[matched_id]["centroid"] = detection["centroid"]
                self.tracks[matched_id]["bbox"] = detection["bbox"]
                self.tracks[matched_id]["last_seen"] = datetime.utcnow()

            track = self.tracks[matched_id]
            prev_y = track["previous_centroid"][1]
            curr_y = track["centroid"][1]

            crossed_down = prev_y < line_y <= curr_y
            crossed_up = prev_y > line_y >= curr_y
            crossed_any = crossed_down or crossed_up

            if crossed_any and not track["counted_passby"]:
                self.passby_count += 1
                track["counted_passby"] = True
            if crossed_down and not track["counted_entry"]:
                self.entry_count += 1
                track["counted_entry"] = True
            if crossed_up and not track["counted_exit"]:
                self.exit_count += 1
                track["counted_exit"] = True

            updated_track_ids.add(matched_id)

        stale_track_ids = []
        for track_id, track in self.tracks.items():
            age = (datetime.utcnow() - track["last_seen"]).total_seconds()
            if track_id not in updated_track_ids and age > 1.6:
                stale_track_ids.append(track_id)

        for track_id in stale_track_ids:
            self.tracks.pop(track_id, None)

    def _build_result(self, visible_count: int, capacity: int, source: str, camera_active: bool, line_y: int) -> Dict[str, object]:
        occupancy_percent = int((visible_count / max(capacity, 1)) * 100)
        confidence = 86 if camera_active else random.randint(62, 79)
        result = {
            "count": visible_count,
            "capacity": capacity,
            "occupancy_percent": occupancy_percent,
            "occupancy_level": self._level_from_percent(occupancy_percent),
            "confidence": confidence,
            "source": source,
            "timestamp": datetime.utcnow().isoformat(),
            "tracking": {
                "camera_active": camera_active,
                "visible_now": visible_count,
                "entered": self.entry_count,
                "exited": self.exit_count,
                "passed_by": self.passby_count,
                "tracking_mode": "line crossing motion tracker" if camera_active else "simulation fallback",
                "line_position": line_y,
                "active_tracks": len(self.tracks),
            },
        }
        self.last_result = result
        return result

    def _build_simulation_frame(self, status: Dict[str, object]) -> np.ndarray:
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[:, :] = (0, 0, 0)
        line_y = 240
        cv2.rectangle(frame, (16, 16), (624, 464), (80, 80, 80), 2)
        cv2.line(frame, (40, line_y), (600, line_y), (7, 193, 255), 2)
        cv2.putText(frame, "ViaVidentis IoT Feed", (32, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.95, (7, 193, 255), 2)
        cv2.putText(frame, "Camera unavailable. Running simulation fallback.", (32, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.72, (255, 255, 255), 2)
        cv2.putText(frame, f"Visible now: {status['tracking']['visible_now']}", (32, 190), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (224, 224, 224), 2)
        cv2.putText(frame, f"Entered: {status['tracking']['entered']}  Passed by: {status['tracking']['passed_by']}", (32, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (224, 224, 224), 2)
        cv2.putText(frame, f"Occupancy: {status['occupancy_percent']}%  Status: {status['occupancy_level']}", (32, 290), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (7, 193, 255), 2)
        cv2.putText(frame, "No faces, videos, or identities are stored.", (32, 420), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (180, 180, 180), 2)
        return frame

    def get_occupancy_count(self, capacity: int = 20, force_simulated: bool = False) -> Dict[str, object]:
        with self.lock:
            if force_simulated:
                return self._simulate_status(capacity)

            if not self._safe_open_camera():
                return self._simulate_status(capacity)

            ok, frame = self.capture.read()
            if not ok:
                self._release_camera()
                return self._simulate_status(capacity)

            detections = self._extract_moving_people(frame)
            line_y = 240
            self._match_tracks(detections, line_y)
            visible_count = len(detections)
            return self._build_result(
                visible_count=visible_count,
                capacity=capacity,
                source="webcam-tracking",
                camera_active=True,
                line_y=line_y,
            )

    def generate_frame(self, capacity: int = 20, force_simulated: bool = False) -> bytes:
        with self.lock:
            if force_simulated or not self._safe_open_camera():
                status = self._simulate_status(capacity)
                frame = self._build_simulation_frame(status)
            else:
                ok, frame = self.capture.read()
                if not ok:
                    self._release_camera()
                    frame = self._build_simulation_frame(self._simulate_status(capacity))
                else:
                    frame = cv2.resize(frame, (640, 480))
                    detections = self._extract_moving_people(frame)
                    line_y = frame.shape[0] // 2
                    self._match_tracks(detections, line_y)
                    status = self._build_result(
                        visible_count=len(detections),
                        capacity=capacity,
                        source="webcam-tracking",
                        camera_active=True,
                        line_y=line_y,
                    )

                    glow_color = (7, 193, 255)
                    cv2.rectangle(frame, (8, 8), (632, 472), glow_color, 3)
                    cv2.line(frame, (24, line_y), (616, line_y), glow_color, 2)
                    cv2.putText(frame, "ACTIVE TRACKING", (24, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.72, glow_color, 2)
                    cv2.putText(frame, "Crossing line counts passers-by and entries", (24, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 255, 255), 1)

                    for track in self.tracks.values():
                        if "bbox" not in track:
                            continue
                        x, y, w, h = track["bbox"]
                        cv2.rectangle(frame, (x, y), (x + w, y + h), glow_color, 2)
                        cv2.circle(frame, track["centroid"], 4, (255, 255, 255), -1)

                    overlay = np.zeros_like(frame)
                    cv2.rectangle(overlay, (16, 376), (624, 464), (0, 0, 0), -1)
                    frame = cv2.addWeighted(frame, 1.0, overlay, 0.28, 0)
                    cv2.putText(frame, f"Visible: {status['tracking']['visible_now']}", (28, 406), cv2.FONT_HERSHEY_SIMPLEX, 0.72, (255, 255, 255), 2)
                    cv2.putText(frame, f"Entered: {status['tracking']['entered']}", (190, 406), cv2.FONT_HERSHEY_SIMPLEX, 0.72, glow_color, 2)
                    cv2.putText(frame, f"Passed By: {status['tracking']['passed_by']}", (328, 406), cv2.FONT_HERSHEY_SIMPLEX, 0.72, glow_color, 2)
                    cv2.putText(frame, f"Occupancy: {status['occupancy_percent']}%", (28, 438), cv2.FONT_HERSHEY_SIMPLEX, 0.68, (224, 224, 224), 2)
                    cv2.putText(frame, f"Status: {status['occupancy_level']}", (232, 438), cv2.FONT_HERSHEY_SIMPLEX, 0.68, (224, 224, 224), 2)
                    cv2.putText(frame, "Anonymous counts only", (454, 438), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (224, 224, 224), 2)

        ok, jpeg = cv2.imencode(".jpg", frame)
        if not ok:
            raise RuntimeError("Unable to encode monitor frame")
        return jpeg.tobytes()


people_counter = PeopleCounter()
