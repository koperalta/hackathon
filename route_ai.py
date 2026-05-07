from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2
from typing import Dict, List

from data_store import get_dashboard_dataset, get_route_lookup, load_routes, load_vehicles, read_logs


def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    radius = 6371.0
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
    return 2 * radius * atan2(sqrt(a), sqrt(1 - a))


def _crowding_from_percent(percent: int) -> str:
    if percent < 50:
        return "Low"
    if percent <= 80:
        return "Medium"
    return "High"


def _peak_factor(now: datetime | None = None) -> float:
    current = now or datetime.now()
    if 6 <= current.hour <= 9 or 17 <= current.hour <= 20:
        return 1.18
    return 1.0


def predict_eta_and_crowding(vehicle_id: str) -> Dict:
    routes = get_route_lookup()
    vehicles = load_vehicles()["vehicles"]
    vehicle = next((item for item in vehicles if item["id"] == vehicle_id), None)
    if not vehicle:
        raise ValueError("Vehicle not found")

    route = routes[vehicle["route_id"]]
    path = route["path"]
    current_index = int(vehicle.get("path_index", 0))
    remaining_points = path[current_index:]

    remaining_distance = 0.0
    if len(remaining_points) > 1:
        for current, nxt in zip(remaining_points, remaining_points[1:]):
            remaining_distance += _haversine_km(current[0], current[1], nxt[0], nxt[1])

    stop_penalty = max(len(route["stops"]) - 1, 1) * 1.2
    traffic_delay = route["traffic_factor"] * _peak_factor()
    load_delay = 1 + (vehicle["occupancy_percent"] / 100) * 0.25
    speed = max(vehicle.get("speed_kph", 15), 8)
    eta_minutes = max(2, round(((remaining_distance / speed) * 60 * traffic_delay * load_delay) + stop_penalty))
    crowding = _crowding_from_percent(vehicle["occupancy_percent"])
    recommendation = "Ride now"
    if vehicle["occupancy_percent"] >= 90:
        recommendation = "Wait for the next vehicle or choose a less crowded route"
    elif vehicle["status"] in {"Delayed", "Offline", "Break"}:
        recommendation = "Consider an alternative route due to service disruption"

    confidence = max(58, min(91, int((route["reliability"] + vehicle.get("confidence", 70)) / 2)))
    return {
        "vehicle_id": vehicle["id"],
        "route_id": route["id"],
        "route_name": route["name"],
        "eta_minutes": eta_minutes,
        "crowding": crowding,
        "crowding_percent": vehicle["occupancy_percent"],
        "recommendation": recommendation,
        "confidence": confidence,
        "fare": route["fare"],
        "mode": route["mode"],
    }


def suggest_smart_route(priority: str = "fastest") -> Dict:
    routes = get_route_lookup()
    vehicles = load_vehicles()["vehicles"]
    evaluated_routes: List[Dict] = []

    for vehicle in vehicles:
        prediction = predict_eta_and_crowding(vehicle["id"])
        route = routes[vehicle["route_id"]]
        crowd_penalty = 20 if vehicle["occupancy_percent"] > 90 else vehicle["occupancy_percent"] * 0.15
        fare_penalty = route["fare"] * 0.55
        wait_bonus = max(0, 15 - prediction["eta_minutes"])
        accessibility_bonus = route["accessibility_score"] * 0.25
        student_bonus = 12 if route["student_friendly"] else 0
        safety_bonus = route["safety_score"] * 0.18
        reliability_bonus = route["reliability"] * 0.22
        score = wait_bonus + accessibility_bonus + reliability_bonus - crowd_penalty - fare_penalty

        if priority == "cheapest":
            score += 18 - route["fare"]
        elif priority == "least_crowded":
            score += max(0, 30 - vehicle["occupancy_percent"])
        elif priority == "student_friendly":
            score += student_bonus + 6
        elif priority == "safest":
            score += safety_bonus + 10
        elif priority == "most_reliable":
            score += reliability_bonus + 8
        else:
            score += max(0, 25 - prediction["eta_minutes"])

        evaluated_routes.append(
            {
                "vehicle_id": vehicle["id"],
                "route_id": route["id"],
                "route_name": route["name"],
                "mode": route["mode"],
                "priority": priority,
                "score": round(score, 2),
                "eta_minutes": prediction["eta_minutes"],
                "fare": route["fare"],
                "occupancy_percent": vehicle["occupancy_percent"],
                "occupancy_level": vehicle["occupancy_level"],
                "status": vehicle["status"],
                "recommendation_reason": _build_reason(priority, prediction, route, vehicle),
            }
        )

    evaluated_routes.sort(key=lambda item: item["score"], reverse=True)
    best = evaluated_routes[0]
    alternatives = evaluated_routes[1:3]
    return {"best_route": best, "alternatives": alternatives, "all_routes": evaluated_routes}


def _build_reason(priority: str, prediction: Dict, route: Dict, vehicle: Dict) -> str:
    if priority == "cheapest":
        return f"{route['name']} keeps fare low at PHP {route['fare']} while staying {vehicle['occupancy_level'].lower()}."
    if priority == "least_crowded":
        return f"{route['name']} is at {vehicle['occupancy_percent']}% occupancy, making it one of the lighter options now."
    if priority == "student_friendly":
        return f"{route['name']} is student-friendly with moderate fare and access near schools and training areas."
    if priority == "safest":
        return f"{route['name']} scores higher on safer stops and more predictable dispatch."
    if priority == "most_reliable":
        return f"{route['name']} has one of the strongest reliability scores and an ETA of {prediction['eta_minutes']} minutes."
    return f"{route['name']} balances ETA ({prediction['eta_minutes']} min), fare, and crowding for today's trip."


def calculate_opportunity_access_score() -> Dict:
    routes_payload = load_routes()
    routes = routes_payload["routes"]
    logs = read_logs()
    report_counts = Counter(log["barangay"] for log in logs if log["event_type"] == "report")
    telemetry_by_barangay: Dict[str, List[Dict]] = defaultdict(list)

    for log in logs:
        telemetry_by_barangay[log["barangay"]].append(log)

    scores = []
    for route in routes:
        for barangay in route["barangays"]:
            local_logs = telemetry_by_barangay.get(barangay, [])
            avg_wait = sum(int(float(log["wait_minutes"])) for log in local_logs) / max(len(local_logs), 1)
            avg_crowding = sum(int(float(log["occupancy_percent"])) for log in local_logs if log["occupancy_percent"]) / max(len(local_logs), 1)
            route_availability = 82 if any(r["id"] == route["id"] for r in routes) else 60
            affordability = max(35, 100 - route["fare"] * 1.2)
            school_access = 78 if route["student_friendly"] else 62
            healthcare_access = route["accessibility_score"]
            reliability = route["reliability"]
            congestion_penalty = avg_crowding * 0.22
            report_penalty = report_counts.get(barangay, 0) * 6
            score = (
                school_access * 0.16
                + healthcare_access * 0.16
                + route_availability * 0.14
                + affordability * 0.12
                + reliability * 0.14
                + max(0, 100 - avg_wait * 6) * 0.14
                + max(0, 100 - congestion_penalty) * 0.14
            ) - report_penalty

            score = max(20, min(96, round(score, 1)))
            scores.append(
                {
                    "barangay": barangay,
                    "route_name": route["name"],
                    "score": score,
                    "label": label_opportunity_score(score),
                    "average_wait": round(avg_wait, 1),
                    "average_crowding": round(avg_crowding, 1),
                }
            )

    scores.sort(key=lambda item: item["score"])
    return {
        "scores": scores,
        "underserved_areas": [item for item in scores if item["score"] < 60][:5],
        "high_access_areas": [item for item in scores if item["score"] >= 80][:5],
    }


def label_opportunity_score(score: float) -> str:
    if score >= 80:
        return "Good access"
    if score >= 60:
        return "Moderate access"
    if score >= 40:
        return "Limited access"
    return "Opportunity gap area"


def dashboard_insights() -> Dict:
    dataset = get_dashboard_dataset()
    opportunity = calculate_opportunity_access_score()
    highest_demand = max(dataset["crowding_by_route"], key=lambda item: item["average_occupancy"])
    longest_wait = max(dataset["crowding_by_route"], key=lambda item: item["average_wait"])

    insights = [
        f"{highest_demand['route_name']} shows the highest average crowding at {highest_demand['average_occupancy']}%.",
        f"{longest_wait['route_name']} has the longest average wait at {longest_wait['average_wait']} minutes.",
    ]

    if opportunity["underserved_areas"]:
        gap = opportunity["underserved_areas"][0]
        insights.append(
            f"{gap['barangay']} is flagged as a priority area with a score of {gap['score']} and {gap['average_wait']} minute average waits."
        )

    dispatch = []
    for route in dataset["crowding_by_route"]:
        if route["average_occupancy"] >= 80:
            dispatch.append(
                {
                    "route_name": route["route_name"],
                    "action": "Increase dispatch during peak hours near schools and work hubs.",
                }
            )
        elif route["average_wait"] >= 12:
            dispatch.append(
                {
                    "route_name": route["route_name"],
                    "action": "Investigate gaps in vehicle availability and stop-level pickup coverage.",
                }
            )

    return {
        "insights": insights,
        "dispatch_recommendations": dispatch[:4],
        "opportunity": opportunity,
        "dataset": dataset,
    }
