from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Generator, Optional, Tuple

import cv2
import numpy as np

try:
    # Ultralytics YOLO (PyTorch) – required for yolo11n.pt
    from ultralytics import YOLO
except Exception:  # pragma: no cover
    YOLO = None  # type: ignore


@dataclass
class PitxStatus:
    timestamp_iso: str
    people_count: int
    inference_ms: int


class PitxVideoProcessor:
    """
    Reads the PITX rush hour video in a loop and runs YOLOv11 person detection.
    Exposes:
      - next_frame_jpeg(): bytes (JPEG with bounding boxes)
      - last_status: PitxStatus

    This is intentionally "demo-optimized":
      - hardcoded to PITX video + person class
      - lightweight state, thread-safe
    """

    def __init__(
        self,
        video_path: str | Path,
        model_path: str | Path,
        resize: Tuple[int, int] = (960, 540),
        conf: float = 0.35,
    ) -> None:
        self.video_path = Path(video_path)
        self.model_path = Path(model_path)
        self.resize = resize
        self.conf = conf

        self._lock = threading.Lock()
        self._cap: Optional[cv2.VideoCapture] = None
        self._model = None

        self.last_status = PitxStatus(
            timestamp_iso=datetime.utcnow().isoformat(),
            people_count=0,
            inference_ms=0,
        )

    def _ensure_ready(self) -> None:
        if self._cap is None:
            self._cap = cv2.VideoCapture(str(self.video_path))
        if self._cap is None or not self._cap.isOpened():
            raise FileNotFoundError(
                f"Unable to open PITX video at '{self.video_path}'. "
                f"Place the file at /workspace/data/pitx_rush_hour.mp4."
            )

        if self._model is None:
            if YOLO is None:
                raise ImportError(
                    "ultralytics is not installed, but required to run yolo11n.pt. "
                    "Install it (and torch) before running the demo."
                )
            self._model = YOLO(str(self.model_path))

    def _loop_video(self) -> None:
        assert self._cap is not None
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def _read_frame(self) -> np.ndarray:
        assert self._cap is not None
        ok, frame = self._cap.read()
        if not ok or frame is None:
            self._loop_video()
            ok, frame = self._cap.read()
        if not ok or frame is None:
            raise RuntimeError("Unable to read frames from PITX video.")
        return frame

    def _infer_people(self, frame: np.ndarray) -> Tuple[int, np.ndarray, int]:
        """
        Returns (people_count, annotated_frame, inference_ms)
        """
        assert self._model is not None

        start = time.perf_counter()

        resized = cv2.resize(frame, self.resize)
        results = self._model(resized, classes=[0], conf=self.conf, verbose=False)

        people_count = 0
        annotated = resized.copy()

        for r in results:
            if r.boxes is None:
                continue
            for box in r.boxes:
                # xyxy is (1,4)
                x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
                people_count += 1
                cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 255), 2)
                cv2.putText(
                    annotated,
                    "person",
                    (x1, max(18, y1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (0, 255, 255),
                    2,
                )

        inference_ms = int((time.perf_counter() - start) * 1000)
        return people_count, annotated, inference_ms

    def next_frame_jpeg(self) -> bytes:
        with self._lock:
            self._ensure_ready()
            frame = self._read_frame()
            people_count, annotated, inference_ms = self._infer_people(frame)

            # Camera-style HUD overlays (kept minimal so the frontend can overlay too)
            hud = annotated.copy()
            cv2.rectangle(hud, (14, 14), (220, 56), (0, 0, 0), -1)
            annotated = cv2.addWeighted(annotated, 1.0, hud, 0.35, 0)

            cv2.putText(annotated, "PITX LIVE", (24, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
            cv2.circle(annotated, (198, 34), 7, (0, 0, 255), -1)

            now_iso = datetime.utcnow().isoformat()
            self.last_status = PitxStatus(timestamp_iso=now_iso, people_count=people_count, inference_ms=inference_ms)

            ok, jpeg = cv2.imencode(".jpg", annotated, [int(cv2.IMWRITE_JPEG_QUALITY), 82])
            if not ok:
                raise RuntimeError("Unable to encode PITX frame as JPEG.")
            return jpeg.tobytes()

    def mjpeg_stream(self, fps_cap: float = 12.0) -> Generator[bytes, None, None]:
        """
        Generator for multipart/x-mixed-replace.
        """
        min_dt = 1.0 / max(fps_cap, 1.0)
        while True:
            start = time.perf_counter()
            frame = self.next_frame_jpeg()
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            elapsed = time.perf_counter() - start
            if elapsed < min_dt:
                time.sleep(min_dt - elapsed)


BASE_DIR = Path(__file__).resolve().parent
PITX_VIDEO_PATH = BASE_DIR / "data" / "pitx_rush_hour.mp4"
YOLO_MODEL_PATH = BASE_DIR / "yolo11n.pt"

pitx_processor = PitxVideoProcessor(
    video_path=PITX_VIDEO_PATH,
    model_path=YOLO_MODEL_PATH,
)

