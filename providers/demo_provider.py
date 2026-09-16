import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import RailwayDataProvider


class DemoRailwayProvider(RailwayDataProvider):
    """Adapter around RailMate's existing data/trains.json demo dataset."""

    def __init__(self, data_file: str = "data/trains.json"):
        self.data_file = Path(data_file)
        if not self.data_file.exists():
            raise FileNotFoundError(
                f"Demo railway data not found: {self.data_file}"
            )
        with self.data_file.open("r", encoding="utf-8") as f:
            self.trains = json.load(f)

    @staticmethod
    def _norm(value: str) -> str:
        return " ".join(str(value).strip().lower().split())

    def _matches_route(self, train: Dict[str, Any], origin: str, destination: str) -> bool:
        o = self._norm(origin)
        d = self._norm(destination)
        train_origin = self._norm(
            train.get("origin") or train.get("from") or train.get("source") or ""
        )
        train_destination = self._norm(
            train.get("destination") or train.get("to") or train.get("dest") or ""
        )

        # The current demo dataset is primarily Mysuru/Mysore -> Chennai.
        # If explicit fields exist, use them. Otherwise accept the current demo route.
        if train_origin and train_destination:
            return o in train_origin or train_origin in o and (
                d in train_destination or train_destination in d
            )
        route_text = self._norm(
            f"{train.get('train_name', '')} {train.get('name', '')}"
        )
        return (
            ("mysore" in o or "mysuru" in o)
            and "chennai" in d
            and ("mysore" in route_text or "mysuru" in route_text)
        )

    def search_trains(
        self, origin: str, destination: str, journey_date: str,
        travel_class: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        results = []
        for train in self.trains:
            if not self._matches_route(train, origin, destination):
                continue

            if travel_class:
                classes = train.get("classes", {})
                if travel_class not in classes:
                    continue

            item = dict(train)
            item["data_source"] = "DEMO"
            item["journey_date"] = journey_date
            item["live"] = False
            results.append(item)

        return results

    def check_availability(self, train_number, journey_date, travel_class):
        train = self._find(train_number)
        classes = train.get("classes", {})
        value = classes.get(travel_class)

        if value is None:
            return {
                "train_number": str(train_number),
                "journey_date": journey_date,
                "class": travel_class,
                "status": "NOT_AVAILABLE",
                "data_source": "DEMO",
                "live": False,
            }

        if isinstance(value, dict):
            status = value.get("status", "UNKNOWN")
            quantity = value.get("available")
        else:
            status = str(value)
            quantity = None

        return {
            "train_number": str(train_number),
            "journey_date": journey_date,
            "class": travel_class,
            "status": status,
            "available": quantity,
            "data_source": "DEMO",
            "live": False,
        }

    def get_fare(self, train_number, journey_date, travel_class):
        train = self._find(train_number)
        value = train.get("classes", {}).get(travel_class)

        fare = None
        if isinstance(value, dict):
            fare = value.get("fare")
        elif isinstance(value, str):
            # Existing demo data may store fare separately.
            fares = train.get("fares", {})
            fare = fares.get(travel_class)

        return {
            "train_number": str(train_number),
            "journey_date": journey_date,
            "class": travel_class,
            "fare": fare,
            "currency": "INR",
            "data_source": "DEMO",
            "live": False,
        }

    def get_schedule(self, train_number, journey_date=None):
        train = self._find(train_number)
        return {
            "train_number": str(train_number),
            "journey_date": journey_date,
            "schedule": train,
            "data_source": "DEMO",
            "live": False,
        }

    def get_train_status(self, train_number, journey_date=None):
        return {
            "train_number": str(train_number),
            "journey_date": journey_date,
            "status": "DEMO_STATUS_ONLY",
            "message": "Live running status is not connected.",
            "data_source": "DEMO",
            "live": False,
        }

    def get_pnr_status(self, pnr):
        return {
            "pnr": str(pnr),
            "status": "DEMO_PNR_ONLY",
            "message": "Live PNR service is not connected.",
            "data_source": "DEMO",
            "live": False,
        }

    def _find(self, train_number):
        target = str(train_number)
        for train in self.trains:
            if str(train.get("train_number", train.get("number", ""))) == target:
                return train
        raise ValueError(f"Demo train not found: {train_number}")
