from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ROUTES_FILE = DATA_DIR / "routes.json"
VEHICLES_FILE = DATA_DIR / "vehicles.json"
LOGS_FILE = DATA_DIR / "mobility_logs.csv"


def _read_json(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _write_json(path: Path, payload: Dict) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)


def load_routes() -> Dict:
    return _read_json(ROUTES_FILE)


def load_vehicles() -> Dict:
    return _read_json(VEHICLES_FILE)


def save_vehicles(payload: Dict) -> None:
    _write_json(VEHICLES_FILE, payload)


def get_route_lookup() -> Dict[str, Dict]:
    routes = load_routes()["routes"]
    return {route["id"]: route for route in routes}


def get_vehicle_lookup() -> Dict[str, Dict]:
    vehicles = load_vehicles()["vehicles"]
    return {vehicle["id"]: vehicle for vehicle in vehicles}


def get_vehicle(vehicle_id: str) -> Optional[Dict]:
    return get_vehicle_lookup().get(vehicle_id)


def _level_from_percent(percent: int) -> str:
    if percent < 50:
        return "Maluwag"
    if percent <= 80:
        return "Medyo puno"
    if percent >= 90:
        return "Siksikan"
    return "Pa-puno"


def append_log(
    vehicle_id: str,
    route_id: str,
    event_type: str,
    occupancy_count: int,
    occupancy_percent: int,
    status: str,
    wait_minutes: int,
    barangay: str,
    report_type: str = "",
    confidence: int = 75,
) -> None:
    timestamp = datetime.utcnow().isoformat()
    with LOGS_FILE.open("a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                timestamp,
                vehicle_id,
                route_id,
                event_type,
                occupancy_count,
                occupancy_percent,
                status,
                wait_minutes,
                barangay,
                report_type,
                confidence,
            ]
        )


def read_logs() -> List[Dict]:
    with LOGS_FILE.open("r", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def update_vehicle_location(vehicle_id: str, occupancy_data: Optional[Dict] = None, status_override: Optional[str] = None) -> Dict:
    routes = get_route_lookup()
    payload = load_vehicles()
    updated_vehicle = None

    for vehicle in payload["vehicles"]:
        if vehicle["id"] != vehicle_id:
            continue

        route = routes[vehicle["route_id"]]
        next_index = (vehicle.get("path_index", 0) + 1) % len(route["path"])
        next_lat, next_lng = route["path"][next_index]
        vehicle["path_index"] = next_index
        vehicle["lat"] = next_lat
        vehicle["lng"] = next_lng
        vehicle["updated_at"] = datetime.utcnow().isoformat()

        if occupancy_data:
            vehicle["occupancy_count"] = occupancy_data["count"]
            vehicle["occupancy_percent"] = occupancy_data["occupancy_percent"]
            vehicle["occupancy_level"] = occupancy_data["occupancy_level"]
            vehicle["confidence"] = occupancy_data["confidence"]

        if status_override:
            vehicle["status"] = status_override

        append_log(
            vehicle_id=vehicle["id"],
            route_id=vehicle["route_id"],
            event_type="telemetry",
            occupancy_count=vehicle["occupancy_count"],
            occupancy_percent=vehicle["occupancy_percent"],
            status=vehicle["status"],
            wait_minutes=max(3, 12 - min(vehicle["speed_kph"] // 2, 8)),
            barangay=route["barangays"][min(next_index, len(route["barangays"]) - 1)],
            confidence=vehicle.get("confidence", 75),
        )
        updated_vehicle = vehicle
        break

    save_vehicles(payload)
    if not updated_vehicle:
        raise ValueError(f"Vehicle {vehicle_id} not found")
    return updated_vehicle


def update_vehicle_status(vehicle_id: str, new_status: str) -> Dict:
    payload = load_vehicles()
    updated_vehicle = None
    for vehicle in payload["vehicles"]:
        if vehicle["id"] == vehicle_id:
            vehicle["status"] = new_status
            vehicle["updated_at"] = datetime.utcnow().isoformat()
            updated_vehicle = vehicle
            break

    if not updated_vehicle:
        raise ValueError(f"Vehicle {vehicle_id} not found")

    save_vehicles(payload)
    append_log(
        vehicle_id=updated_vehicle["id"],
        route_id=updated_vehicle["route_id"],
        event_type="status_update",
        occupancy_count=updated_vehicle["occupancy_count"],
        occupancy_percent=updated_vehicle["occupancy_percent"],
        status=updated_vehicle["status"],
        wait_minutes=0,
        barangay="Status Center",
        confidence=updated_vehicle.get("confidence", 75),
    )
    return updated_vehicle


def advance_all_vehicles() -> List[Dict]:
    payload = load_vehicles()
    save_vehicles(payload)
    vehicle_ids = [vehicle["id"] for vehicle in payload["vehicles"]]
    return [update_vehicle_location(vehicle_id) for vehicle_id in vehicle_ids]


def submit_commuter_report(report: Dict) -> Dict:
    vehicles = get_vehicle_lookup()
    routes = get_route_lookup()
    vehicle = vehicles.get(report["vehicle_id"])
    if not vehicle:
        raise ValueError("Unknown vehicle")

    route = routes[vehicle["route_id"]]
    append_log(
        vehicle_id=vehicle["id"],
        route_id=vehicle["route_id"],
        event_type="report",
        occupancy_count=vehicle["occupancy_count"],
        occupancy_percent=vehicle["occupancy_percent"],
        status=vehicle["status"],
        wait_minutes=int(report.get("wait_minutes", 10)),
        barangay=report.get("barangay", route["barangays"][0]),
        report_type=report["report_type"],
        confidence=vehicle.get("confidence", 75),
    )
    return {
        "message": "Commuter report recorded",
        "report_type": report["report_type"],
        "vehicle_id": vehicle["id"],
    }


def get_dashboard_dataset() -> Dict:
    routes = get_route_lookup()
    vehicles = load_vehicles()["vehicles"]
    
    # Load logs natively into a Pandas DataFrame
    try:
        df = pd.read_csv(LOGS_FILE)
    except FileNotFoundError:
        # Fallback empty dataframe matching the CSV columns from append_log
        df = pd.DataFrame(columns=[
            "timestamp", "vehicle_id", "route_id", "event_type", 
            "occupancy_count", "occupancy_percent", "status", 
            "wait_minutes", "barangay", "report_type", "confidence"
        ])

    crowding_by_route = []
    
    if not df.empty:
        # Ensure numerical types for aggregation
        df['occupancy_percent'] = pd.to_numeric(df['occupancy_percent'], errors='coerce')
        df['wait_minutes'] = pd.to_numeric(df['wait_minutes'], errors='coerce')
        
        # Vectorized groupby: Calculate averages in a single pass
        agg_df = df.groupby('route_id').agg(
            average_occupancy=('occupancy_percent', 'mean'),
            average_wait=('wait_minutes', 'mean')
        ).reset_index()
        
        for _, row in agg_df.iterrows():
            route_id = row['route_id']
            if route_id in routes:
                avg_occ = row['average_occupancy']
                avg_wait = row['average_wait']
                
                crowding_by_route.append({
                    "route_id": route_id,
                    "route_name": routes[route_id]["name"],
                    # Clean up NaNs to 0.0 for JSON serialization
                    "average_occupancy": round(avg_occ, 1) if pd.notna(avg_occ) else 0.0,
                    "average_wait": round(avg_wait, 1) if pd.notna(avg_wait) else 0.0,
                    "reliability": routes[route_id]["reliability"],
                })

    # Catch any routes that haven't generated telemetry logs yet
    processed_route_ids = {r["route_id"] for r in crowding_by_route}
    for route_id, route in routes.items():
        if route_id not in processed_route_ids:
            crowding_by_route.append({
                "route_id": route_id,
                "route_name": route["name"],
                "average_occupancy": 0.0,
                "average_wait": 0.0,
                "reliability": route["reliability"],
            })

    return {
        "routes": list(routes.values()),
        "vehicles": vehicles,
        # Convert df back to dict records so the existing frontend doesn't break
        "logs": df.to_dict(orient="records") if not df.empty else [], 
        "crowding_by_route": crowding_by_route,
    }


def normalize_vehicle_occupancy(vehicle: Dict) -> Dict:
    capacity = max(int(vehicle.get("capacity", 1)), 1)
    percent = int(round((int(vehicle.get("occupancy_count", 0)) / capacity) * 100))
    vehicle["occupancy_percent"] = percent
    vehicle["occupancy_level"] = _level_from_percent(percent)
    return vehicle