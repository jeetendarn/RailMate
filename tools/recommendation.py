from datetime import datetime
from typing import Optional


def parse_time(value: str) -> Optional[int]:
    """Convert HH:MM into minutes from midnight."""
    try:
        hour, minute = map(int, value.split(":"))
        return hour * 60 + minute
    except Exception:
        return None


def duration_minutes(duration: str) -> int:
    """Convert '9h 55m' into minutes."""
    try:
        hours = 0
        minutes = 0

        parts = duration.lower().replace(" ", "").split("h")

        if parts[0]:
            hours = int(parts[0])

        if len(parts) > 1 and parts[1]:
            minutes = int(parts[1].replace("m", ""))

        return hours * 60 + minutes
    except Exception:
        return 9999


def is_evening(time_str: str) -> bool:
    value = parse_time(time_str)
    if value is None:
        return False
    return 17 * 60 <= value <= 22 * 60


def is_morning(time_str: str) -> bool:
    value = parse_time(time_str)
    if value is None:
        return False
    return 5 * 60 <= value < 12 * 60


def is_afternoon(time_str: str) -> bool:
    value = parse_time(time_str)
    if value is None:
        return False
    return 12 * 60 <= value < 17 * 60


def is_night(time_str: str) -> bool:
    value = parse_time(time_str)
    if value is None:
        return False
    return value >= 20 * 60 or value < 5 * 60


def _field(train, name, default=None):
    """Read a train field from either a dict or an object."""
    if isinstance(train, dict):
        return train.get(name, default)
    return getattr(train, name, default)


def get_fare(train, travel_class: str):
    fares = _field(train, "fares", {}) or {}
    return fares.get(travel_class)


def get_availability(train, travel_class: str):
    availability = _field(train, "availability", {}) or {}
    return availability.get(travel_class, "NOT AVAILABLE")


def is_confirmed(availability: str) -> bool:
    if not availability:
        return False

    value = availability.upper()

    return (
        "AVAILABLE" in value
        and "NOT AVAILABLE" not in value
        and "RAC" not in value
        and "WL" not in value
        and "WAIT" not in value
    )


def is_bookable(availability: str) -> bool:
    if not availability:
        return False

    value = availability.upper()

    return (
        value != "NOT AVAILABLE"
        and "WAITLIST" not in value
        and "WL" not in value
    )


def calculate_score(train, travel_class: str, preference: Optional[str] = None):
    availability = get_availability(train, travel_class)
    fare = get_fare(train, travel_class)

    if availability == "NOT AVAILABLE":
        return -999

    if fare is None:
        return -999

    score = 0

    # Availability
    if is_confirmed(availability):
        score += 50
    elif "RAC" in availability.upper():
        score += 15
    else:
        score += 5

    # Lower fare gets a better score
    if fare <= 1000:
        score += 25
    elif fare <= 1500:
        score += 20
    elif fare <= 2000:
        score += 10
    else:
        score += 5

    # Shorter duration
    duration = duration_minutes(_field(train, "duration", ""))

    if duration <= 600:
        score += 20
    elif duration <= 720:
        score += 15
    elif duration <= 900:
        score += 10
    else:
        score += 5

    # Fewer stops
    stops = _field(train, "stops", 9999)
    if stops <= 8:
        score += 10
    elif stops <= 12:
        score += 7
    else:
        score += 3

    # Time preference
    if preference:
        preference = preference.lower()

        departure = _field(train, "departure", "")

        if preference == "evening" and is_evening(departure):
            score += 20

        elif preference == "morning" and is_morning(departure):
            score += 20

        elif preference == "afternoon" and is_afternoon(departure):
            score += 20

        elif preference == "night" and is_night(departure):
            score += 20

    return score


def build_option(train, travel_class: str, passengers: int, preference=None):
    availability = get_availability(train, travel_class)
    fare = get_fare(train, travel_class)

    if availability == "NOT AVAILABLE" or fare is None:
        return None

    score = calculate_score(
        train,
        travel_class,
        preference
    )

    return {
        "train_number": _field(train, "train_number"),
        "train_name": _field(train, "train_name"),
        "departure": _field(train, "departure"),
        "arrival": _field(train, "arrival"),
        "duration": _field(train, "duration"),
        "travel_class": travel_class,
        "availability": availability,
        "fare_per_passenger": fare,
        "total_fare": fare * passengers,
        "score": score,
    }


def recommend_trains(
    trains,
    travel_class: str,
    passengers: int = 1,
    preference: Optional[str] = None,
):
    """
    Deterministic recommendation engine.

    Python is the authority for:
    - availability
    - fare
    - ranking
    - recommendation
    """

    options = []

    for train in trains:
        option = build_option(
            train,
            travel_class,
            passengers,
            preference
        )

        if option:
            options.append(option)

    options.sort(
        key=lambda x: (
            x["score"],
            -x["fare_per_passenger"],
        ),
        reverse=True
    )

    return options


def find_cheapest(options):
    if not options:
        return None

    return min(
        options,
        key=lambda x: x["fare_per_passenger"]
    )


def find_fastest(options):
    if not options:
        return None

    return min(
        options,
        key=lambda x: duration_minutes(x["duration"])
    )


def find_earliest(options):
    if not options:
        return None

    return min(
        options,
        key=lambda x: parse_time(x["departure"]) or 9999
    )


def find_latest(options):
    if not options:
        return None

    return max(
        options,
        key=lambda x: parse_time(x["departure"]) or -1
    )


def filter_confirmed(options):
    return [
        option
        for option in options
        if is_confirmed(option["availability"])
    ]


def filter_after_time(options, time_value: str):
    target = parse_time(time_value)

    if target is None:
        return options

    return [
        option
        for option in options
        if (parse_time(option["departure"]) or 0) >= target
    ]


def filter_before_arrival(options, time_value: str):
    target = parse_time(time_value)

    if target is None:
        return options

    return [
        option
        for option in options
        if (parse_time(option["arrival"]) or 9999) <= target
    ]


def compare_trains(options, train_numbers):
    selected = []

    for option in options:
        if str(option["train_number"]) in [
            str(number) for number in train_numbers
        ]:
            selected.append(option)

    return selected


def find_alternatives(options, selected_train_number):
    return [
        option
        for option in options
        if str(option["train_number"]) != str(selected_train_number)
    ]