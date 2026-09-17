import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import RailwayDataProvider


class DemoRailwayProvider(RailwayDataProvider):
    """Adapter for RailMate's existing data/trains.json demo dataset."""

    def __init__(self, data_file: str = "data/trains.json"):
        self.data_file = Path(data_file)
        if not self.data_file.exists():
            raise FileNotFoundError(f"Demo railway data not found: {self.data_file}")

        with self.data_file.open("r", encoding="utf-8") as f:
            self.trains = json.load(f)

    @staticmethod
    def _norm(value: str) -> str:
        value = str(value or "").strip().lower()
        value = value.replace("mysore", "mysuru")
        return " ".join(value.split())

    def _matches_route(
        self,
        train: Dict[str, Any],
        origin: str,
        destination: str,
    ) -> bool:
        requested_origin = self._norm(origin)
        requested_destination = self._norm(destination)

        train_origin = self._norm(train.get("origin", ""))
        train_destination = self._norm(train.get("destination", ""))

        return (
            requested_origin == train_origin
            and requested_destination == train_destination
        )

    def search_trains(
        self,
        origin: str,
        destination: str,
        journey_date: str,
        travel_class: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        results = []

        for train in self.trains:
            if not self._matches_route(train, origin, destination):
                continue

            availability = train.get("availability", {})

            if travel_class and travel_class not in availability:
                continue

            item = dict(train)
            item["data_source"] = "DEMO"
            item["live"] = False
            item["journey_date"] = journey_date
            results.append(item)

        return results

    def _find(self, train_number: str) -> Dict[str, Any]:
        target = str(train_number)

        for train in self.trains:
            if str(train.get("train_number", "")) == target:
                return train

        raise ValueError(f"Demo train not found: {train_number}")

    def check_availability(
        self,
        train_number: str,
        journey_date: str,
        travel_class: str,
    ) -> Dict[str, Any]:
        train = self._find(train_number)
        status = train.get("availability", {}).get(travel_class)

        if status is None:
            status = "NOT_AVAILABLE"

        return {
            "train_number": str(train_number),
            "journey_date": journey_date,
            "class": travel_class,
            "status": status,
            "data_source": "DEMO",
            "live": False,
        }

    def get_fare(
        self,
        train_number: str,
        journey_date: str,
        travel_class: str,
    ) -> Dict[str, Any]:
        train = self._find(train_number)
        fare = train.get("fares", {}).get(travel_class)

        return {
            "train_number": str(train_number),
            "journey_date": journey_date,
            "class": travel_class,
            "fare": fare,
            "currency": "INR",
            "data_source": "DEMO",
            "live": False,
        }

    def get_schedule(
        self,
        train_number: str,
        journey_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        train = self._find(train_number)

        return {
            "train_number": str(train_number),
            "journey_date": journey_date,
            "schedule": train,
            "data_source": "DEMO",
            "live": False,
        }

    def get_train_status(
        self,
        train_number: str,
        journey_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        self._find(train_number)

        return {
            "train_number": str(train_number),
            "journey_date": journey_date,
            "status": "DEMO_STATUS_ONLY",
            "message": "Live running status is not connected.",
            "data_source": "DEMO",
            "live": False,
        }

    def get_pnr_status(self, pnr: str) -> Dict[str, Any]:
        return {
            "pnr": str(pnr),
            "status": "DEMO_PNR_ONLY",
            "message": "Live PNR service is not connected.",
            "data_source": "DEMO",
            "live": False,
        }
