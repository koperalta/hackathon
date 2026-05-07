# transit_api.py
from __future__ import annotations
import json
import urllib.request
from datetime import datetime
from typing import Dict, List, Optional

class TransitAPIClient:
    """
    Client for fetching real-world telemetry from Philippine Bus APIs 
    (e.g., DOTR/LTFRB GTFS-Realtime or Operator-specific JSON feeds).
    """
    def __init__(self, api_endpoint: str = "https://api.transit.gov.ph/v1/fleet"):
        self.api_endpoint = api_endpoint
        self.timeout = 5

    def fetch_live_telemetry(self) -> List[Dict]:
        """
        Connects to the external API and pulls current GPS and status.
        """
        try:
            with urllib.request.urlopen(self.api_endpoint, timeout=self.timeout) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    # Standardizing external data to ViaVidentis schema
                    return self._normalize_feed(data)
        except Exception as e:
            print(f"Error connecting to Transit API: {e}")
            return []
        return []

    def _normalize_feed(self, external_data: Dict) -> List[Dict]:
        """
        Maps external API fields to BiyaheIQ/ViaVidentis fields.
        """
        normalized = []
        # Assumption: External API returns a list of vehicles under 'entities' or 'vehicles'
        vehicles = external_data.get("vehicles", external_data.get("entities", []))
        
        for v in vehicles:
            normalized.append({
                "id": v.get("vehicle_id") or v.get("id"),
                "lat": v.get("latitude") or v.get("lat"),
                "lng": v.get("longitude") or v.get("lng"),
                "speed_kph": v.get("speed", 0),
                "heading": v.get("bearing", 0),
                "status": "In Transit" if v.get("speed", 0) > 0 else "Stationary",
                "last_sync": datetime.utcnow().isoformat()
            })
        return normalized

transit_client = TransitAPIClient()