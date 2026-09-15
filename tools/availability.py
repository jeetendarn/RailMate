from .train_search import load_trains


def check_availability(train_number: str, travel_class: str):
    trains = load_trains()

    travel_class = travel_class.upper()

    for train in trains:
        if train["train_number"] == train_number:
            availability = train["availability"].get(
                travel_class,
                "NOT AVAILABLE"
            )

            fare = train["fares"].get(
                travel_class,
                None
            )

            return {
                "train_number": train_number,
                "class": travel_class,
                "availability": availability,
                "fare": fare
            }

    return {
        "error": "Train not found"
    }