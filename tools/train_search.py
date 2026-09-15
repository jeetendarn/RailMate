import json
from pathlib import Path


DATA_FILE = Path(__file__).parent.parent / "data" / "trains.json"


def load_trains():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def normalize_station(name: str) -> str:
    name = name.lower().strip()

    aliases = {
        "mysore": "mysuru",
        "mysuru": "mysuru",
        "bangalore": "bengaluru",
        "bengaluru": "bengaluru",
        "madras": "chennai",
        "chennai": "chennai"
    }

    return aliases.get(name, name)


def search_trains(origin: str, destination: str):
    trains = load_trains()

    origin_normalized = normalize_station(origin)
    destination_normalized = normalize_station(destination)

    results = []

    for train in trains:
        train_origin = normalize_station(train["origin"])
        train_destination = normalize_station(train["destination"])

        if (
            train_origin == origin_normalized
            and train_destination == destination_normalized
        ):
            results.append(train)

    return results