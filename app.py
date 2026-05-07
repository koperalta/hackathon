from __future__ import annotations

from datetime import datetime
from pathlib import Path

from flask import Flask, Response, jsonify, render_template

from forecasting_ai import pitx_forecaster
from people_counter import pitx_processor
from route_ai import pitx_alternative_route


BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__, template_folder=str(BASE_DIR / "templates"), static_folder=str(BASE_DIR / "static"))


@app.route("/")
def index():
    # Keep the project "front door" template if you have it.
    # If not present, Flask will raise a template error (expected in a real repo).
    return render_template("index.html")


@app.route("/commuter")
def commuter():
    # PITX-only commuter view for the demo.
    return render_template("commuter.html")


@app.route("/video_feed")
def video_feed():
    """
    MJPEG stream with YOLO bounding boxes drawn on PITX video frames.
    """
    return Response(
        pitx_processor.mjpeg_stream(fps_cap=12.0),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@app.route("/api/pitx-status")
def api_pitx_status():
    """
    Single source of truth for the PITX demo UI.
    """
    status = pitx_processor.last_status
    prediction = pitx_forecaster.predict(status.people_count)
    suggestion = pitx_alternative_route(prediction.estimated_wait_minutes, status.people_count)

    return jsonify(
        {
            "terminal": {
                "id": "PITX",
                "name": "PITX Terminal",
                "camera": "Gate 3 (Demo Feed)",
            },
            "live": {
                "timestamp_iso": status.timestamp_iso,
                "timestamp_label": datetime.fromisoformat(status.timestamp_iso).strftime("%b %d • %I:%M:%S %p"),
                "people_count": status.people_count,
                "inference_ms": status.inference_ms,
            },
            "prediction": {
                "estimated_wait_minutes": prediction.estimated_wait_minutes,
                "service_level": prediction.service_level,
            },
            "route_suggestion": suggestion,
        }
    )


if __name__ == "__main__":
    # Demo-friendly host/port
    app.run(debug=True, host="0.0.0.0", port=5001)

