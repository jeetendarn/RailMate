from typing import List
from agent.schemas import TrainOption


def parse_time(time_string: str) -> int:
    """
    Convert HH:MM into minutes after midnight.
    """

    hour, minute = map(int, time_string.split(":"))
    return hour * 60 + minute


def is_evening(time_string: str) -> bool:
    minutes = parse_time(time_string)
    return 17 * 60 <= minutes <= 22 * 60


def is_morning(time_string: str) -> bool:
    minutes = parse_time(time_string)
    return 5 * 60 <= minutes <= 12 * 60


def is_afternoon(time_string: str) -> bool:
    minutes = parse_time(time_string)
    return 12 * 60 <= minutes <= 17 * 60


def calculate_score(
    train,
    travel_class: str,
    preference: str | None = None,
    arrival_before: str | None = None,
):
    score = 0

    availability = train["availability"].get(travel_class, "NOT AVAILABLE")
    fare = train["fares"].get(travel_class)

    # Availability
    if availability == "AVAILABLE":
        score += 40
    elif availability.startswith("RAC"):
        score += 10
    else:
        return -999

    # Fare
    if fare is not None:
        if fare <= 1500:
            score += 20
        elif fare <= 2000:
            score += 10

    # Duration
    duration_parts = train["duration"].replace("h", "").replace("m", "").split()

    try:
        hours = int(duration_parts[0])
        minutes = int(duration_parts[1])
        duration_minutes = hours * 60 + minutes
    except Exception:
        duration_minutes = 9999

    if duration_minutes <= 600:
        score += 20
    elif duration_minutes <= 720:
        score += 10

    # Stops
    stops = train.get("stops", 20)

    if stops <= 10:
        score += 10
    elif stops <= 15:
        score += 5

    # User time preference
    departure = train["departure"]

    if preference == "evening":
        if is_evening(departure):
            score += 25

    elif preference == "morning":
        if is_morning(departure):
            score += 25

    elif preference == "afternoon":
        if is_afternoon(departure):
            score += 25

    elif preference == "night":
        if parse_time(departure) >= 20 * 60:
            score += 25

    # Arrival deadline
    if arrival_before:
        if parse_time(train["arrival"]) <= parse_time(arrival_before):
            score += 20
        else:
            score -= 30

    return score


def recommend_trains(
    trains: List[dict],
    travel_class: str,
    passengers: int,
    preference: str | None = None,
    arrival_before: str | None = None,
):
    results = []

    for train in trains:

        availability = train["availability"].get(
            travel_class,
            "NOT AVAILABLE"
        )

        fare = train["fares"].get(travel_class)

        # Never show unavailable trains
        if availability == "NOT AVAILABLE":
            continue

        # Never show missing fare
        if fare is None:
            continue

        score = calculate_score(
            train,
            travel_class,
            preference,
            arrival_before,
        )

        if score < 0:
            continue

        total_fare = fare * passengers

        option = TrainOption(
            train_number=train["train_number"],
            train_name=train["train_name"],
            departure=train["departure"],
            arrival=train["arrival"],
            duration=train["duration"],
            travel_class=travel_class,
            availability=availability,
            fare_per_passenger=fare,
            total_fare=total_fare,
            score=score,
        )

        results.append(option)

    # Highest score first
    results.sort(
        key=lambda x: (
            x.score,
            x.availability == "AVAILABLE",
            -(x.fare_per_passenger or 999999),
        ),
        reverse=True,
    )

    return results