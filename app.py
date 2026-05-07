from __future__ import annotations

import time
import random
from pathlib import Path

from flask import Flask, Response, jsonify, render_template, request

from data_store import (
    get_dashboard_dataset,
    get_route_lookup,
    get_vehicle,
    load_vehicles,
    submit_commuter_report,
    update_vehicle_location,
    update_vehicle_status,
)
from people_counter import people_counter
from route_ai import calculate_opportunity_access_score, dashboard_insights, predict_eta_and_crowding, suggest_smart_route


BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__, template_folder=str(BASE_DIR / "templates"), static_folder=str(BASE_DIR / "static"))


# --- Helper Function for IoT Simulation ---
def simulate_iot_latency(min_sec: float = 0.3, max_sec: float = 0.8) -> None:
    """
    Introduces a random artificial delay to mimic the network latency 
    of edge devices (like cameras) transmitting data over cellular networks.
    """
    time.sleep(random.uniform(min_sec, max_sec))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/monitor")
def monitor():
    return render_template("monitor.html")


@app.route("/commuter")
def commuter():
    return render_template("commuter.html")


@app.route("/dashboard")
def dashboard():
    return render_template("lgu_dashboard.html")


@app.route("/api/vehicles")
def api_vehicles():
    # Simulate database/network fetch latency for fleet telemetry
    simulate_iot_latency(0.2, 0.5)
    
    vehicles = load_vehicles()["vehicles"]
    routes = get_route_lookup()
    enriched = []
    for vehicle in vehicles:
        prediction = predict_eta_and_crowding(vehicle["id"])
        route = routes[vehicle["route_id"]]
        vehicle_payload = dict(vehicle)
        vehicle_payload["prediction"] = prediction
        vehicle_payload["route_name"] = route["name"]
        vehicle_payload["route_path"] = route["path"]
        vehicle_payload["stops"] = route["stops"]
        enriched.append(vehicle_payload)
    return jsonify({"vehicles": enriched})


@app.route("/api/monitor/status", methods=["GET", "POST"])
def api_monitor_status():
    # Simulate the critical edge computing delay from the YOLOv11 camera node
    simulate_iot_latency(0.4, 0.9)
    
    payload = request.get_json(silent=True) or {}
    vehicle_id = payload.get("vehicle_id") or request.args.get("vehicle_id", "JEEP-001")
    simulate = payload.get("simulate", request.args.get("simulate", "false").lower() == "true")
    vehicle = get_vehicle(vehicle_id)
    if not vehicle:
        return jsonify({"error": "Vehicle not found"}), 404

    occupancy = people_counter.get_occupancy_count(capacity=vehicle["capacity"], force_simulated=simulate)
    updated_vehicle = update_vehicle_location(vehicle_id, occupancy_data=occupancy)
    prediction = predict_eta_and_crowding(vehicle_id)
    return jsonify({"vehicle": updated_vehicle, "occupancy": occupancy, "prediction": prediction})


@app.route("/api/monitor/frame")
def api_monitor_frame():
    vehicle_id = request.args.get("vehicle_id", "JEEP-001")
    simulate = request.args.get("simulate", "false").lower() == "true"
    vehicle = get_vehicle(vehicle_id)
    capacity = vehicle["capacity"] if vehicle else 20

    def stream():
        while True:
            # MJPEG streaming handles its own pacing, but we can add a tiny tick
            # to simulate frame encoding/transmission time from the edge node
            time.sleep(0.05) 
            frame = people_counter.generate_frame(capacity=capacity, force_simulated=simulate)
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"

    return Response(stream(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/api/monitor/reset", methods=["POST"])
def api_monitor_reset():
    simulate_iot_latency(0.2, 0.4)
    payload = request.get_json(silent=True) or {}
    vehicle_id = payload.get("vehicle_id", "JEEP-001")
    vehicle = get_vehicle(vehicle_id)
    if not vehicle:
        return jsonify({"error": "Vehicle not found"}), 404

    occupancy = people_counter.reset_tracking()
    prediction = predict_eta_and_crowding(vehicle_id)
    return jsonify({"vehicle": vehicle, "occupancy": occupancy, "prediction": prediction})


@app.route("/api/vehicle/<vehicle_id>/status", methods=["POST"])
def api_vehicle_status(vehicle_id: str):
    simulate_iot_latency(0.3, 0.6)
    payload = request.get_json(force=True)
    new_status = payload.get("status")
    if not new_status:
        return jsonify({"error": "Missing status"}), 400
    vehicle = update_vehicle_status(vehicle_id, new_status)
    prediction = predict_eta_and_crowding(vehicle_id)
    return jsonify({"vehicle": vehicle, "prediction": prediction})


@app.route("/api/commuter/recommendation")
def api_commuter_recommendation():
    # Simulate processing time for the routing AI traversing live data
    simulate_iot_latency(0.5, 1.0)
    priority = request.args.get("priority", "fastest")
    recommendation = suggest_smart_route(priority=priority)
    return jsonify(recommendation)


@app.route("/api/commuter/report", methods=["POST"])
def api_commuter_report():
    simulate_iot_latency(0.2, 0.5)
    payload = request.get_json(force=True)
    result = submit_commuter_report(payload)
    return jsonify(result)


@app.route("/api/dashboard/summary")
def api_dashboard_summary():
    # Heavier endpoints simulate a larger data aggregation payload
    simulate_iot_latency(0.6, 1.2)
    insights = dashboard_insights()
    opportunity = calculate_opportunity_access_score()
    return jsonify(
        {
            "route_metrics": insights["dataset"]["crowding_by_route"],
            "vehicles": insights["dataset"]["vehicles"],
            "insights": insights["insights"],
            "dispatch_recommendations": insights["dispatch_recommendations"],
            "opportunity_scores": opportunity["scores"],
            "underserved_areas": opportunity["underserved_areas"],
        }
    )


@app.route("/api/opportunity-score")
def api_opportunity_score():
    simulate_iot_latency(0.4, 0.8)
    return jsonify(calculate_opportunity_access_score())


if __name__ == "__main__":
    # Changed from 5000 to 5001 to avoid macOS AirPlay conflicts
    app.run(debug=True, host="0.0.0.0", port=5001)