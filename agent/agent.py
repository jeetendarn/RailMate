import json
import re
from datetime import datetime

import ollama

from agent.prompts import SYSTEM_PROMPT
from agent.schemas import TravelRequest
from tools.train_search import search_trains
from tools.recommendation import recommend_trains


MODEL = "llama3.2"


CURRENT_DATE = datetime(2026, 9, 15)


def normalize_city(city):
    """
    Normalize common Indian city names.
    """

    if not city:
        return city

    city = city.strip()

    aliases = {
        "mysore": "Mysore",
        "mysuru": "Mysore",
        "bangalore": "Bangalore",
        "bengaluru": "Bangalore",
        "chennai": "Chennai",
    }

    return aliases.get(city.lower(), city.title())


def normalize_class(value):
    if not value:
        return value

    value = value.upper().strip()

    aliases = {
        "2 AC": "2A",
        "AC 2": "2A",
        "2A": "2A",
        "THIRD AC": "3A",
        "3 AC": "3A",
        "AC 3": "3A",
        "3A": "3A",
        "FIRST AC": "1A",
        "1 AC": "1A",
        "1A": "1A",
        "SLEEPER": "SL",
        "SL": "SL",
        "CHAIR CAR": "CC",
        "CC": "CC",
    }

    return aliases.get(value, value)


def normalize_passengers(value):
    """
    Convert values such as:

    2
    "2"
    "2 people"
    "two people"

    into an integer.
    """

    if value is None:
        return None

    if isinstance(value, int):
        return value

    if isinstance(value, float):
        return int(value)

    text = str(value).lower().strip()

    number_words = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
    }

    for word, number in number_words.items():
        if word in text:
            return number

    match = re.search(r"\d+", text)

    if match:
        return int(match.group())

    return None


def normalize_date(value):
    """
    Normalize common date expressions.

    Current prototype date:
    September 15, 2026
    """

    if not value:
        return None

    text = str(value).strip().lower()

    if text == "today":
        return "2026-09-15"

    if text == "tomorrow":
        return "2026-09-16"

    if text in ["day after tomorrow", "day-after-tomorrow"]:
        return "2026-09-17"

    # Already ISO
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        return text

    # September 21 / Sep 21
    formats = [
        "%B %d",
        "%b %d",
        "%d %B",
        "%d %b",
    ]

    for fmt in formats:
        try:
            parsed = datetime.strptime(text, fmt)

            return parsed.replace(
                year=2026
            ).strftime("%Y-%m-%d")

        except ValueError:
            pass

    return value


def clean_request(request: TravelRequest) -> TravelRequest:

    request.origin = normalize_city(request.origin)
    request.destination = normalize_city(request.destination)

    request.passengers = normalize_passengers(
        request.passengers
    )

    request.travel_class = normalize_class(
        request.travel_class
    )

    request.journey_date = normalize_date(
        request.journey_date
    )

    if request.preference:
        request.preference = request.preference.lower().strip()

    return request


def merge_requests(old_request, new_request):

    data = old_request.model_dump()

    new_data = new_request.model_dump()

    for key, value in new_data.items():

        if value is not None:
            data[key] = value

    return TravelRequest(**data)


def extract_request(
    user_message: str,
    existing_request: TravelRequest | None = None,
):

    if existing_request is None:
        existing_request = TravelRequest()

    prompt = f"""
{SYSTEM_PROMPT}

Current known travel information:

{existing_request.model_dump_json(indent=2)}

User message:

{user_message}

Extract ONLY information explicitly stated or clearly implied
by the user's message.

Return JSON with these fields:

origin
destination
journey_date
passengers
travel_class
departure_time
arrival_before
preference

For unknown fields return null.

IMPORTANT:

If the user says:
"evening"
"in the evening"
"evening time"

return:

"preference": "evening"

If the user says:
"morning"
"in the morning"

return:

"preference": "morning"

If the user says:
"afternoon"
"in the afternoon"

return:

"preference": "afternoon"

If the user says:
"night"
"at night"

return:

"preference": "night"

Do not add explanations.
"""

    try:

        response = ollama.chat(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            format="json",
        )

        content = response["message"]["content"]

        data = json.loads(content)

        new_request = TravelRequest(**data)

        merged = merge_requests(
            existing_request,
            new_request,
        )

        # ----------------------------------------------------------
        # DETERMINISTIC BACKUP EXTRACTION
        # ----------------------------------------------------------

        text = user_message.lower()

        # Time preferences
        if (
            "evening" in text
            or "after 5 pm" in text
            or "after 5pm" in text
        ):
            merged.preference = "evening"

        elif "morning" in text:
            merged.preference = "morning"

        elif "afternoon" in text:
            merged.preference = "afternoon"

        elif "night" in text:
            merged.preference = "night"

        # Passenger backup
        passenger_patterns = [
            r"(\d+)\s*people",
            r"(\d+)\s*passengers",
            r"for\s*(\d+)",
        ]

        for pattern in passenger_patterns:

            match = re.search(pattern, text)

            if match:
                merged.passengers = int(
                    match.group(1)
                )
                break

        return clean_request(merged)

    except Exception as e:

        print(
            f"\n[Warning: AI extraction failed: {e}]"
        )

        # ----------------------------------------------------------
        # Even if Ollama fails completely, preserve state
        # ----------------------------------------------------------

        text = user_message.lower()

        if "evening" in text:
            existing_request.preference = "evening"

        elif "morning" in text:
            existing_request.preference = "morning"

        elif "afternoon" in text:
            existing_request.preference = "afternoon"

        elif "night" in text:
            existing_request.preference = "night"

        match = re.search(
            r"(\d+)\s*(people|passengers)",
            text,
        )

        if match:
            existing_request.passengers = int(
                match.group(1)
            )

        return clean_request(existing_request)
    
def missing_information(request):

    missing = []

    if not request.origin:
        missing.append("origin")

    if not request.destination:
        missing.append("destination")

    if not request.journey_date:
        missing.append("journey_date")

    if not request.passengers:
        missing.append("passengers")

    if not request.travel_class:
        missing.append("travel_class")

    return missing


def generate_question(missing):

    questions = {
        "origin": "Where are you travelling from?",
        "destination": "Where would you like to travel to?",
        "journey_date": "What date would you like to travel?",
        "passengers": "How many passengers will be travelling?",
        "travel_class": "Which class would you like — 1A, 2A, 3A, SL or CC?",
    }

    if not missing:
        return None

    # Defensive handling:
    # If a single field name is passed instead of a list,
    # convert it into a list first.
    if isinstance(missing, str):
        missing = [missing]

    return questions.get(
        missing[0],
        "What additional travel information would you like to provide?"
    )

    
def search_and_recommend(request):

    trains = search_trains(
        request.origin,
        request.destination,
    )

    if not trains:
        return []

    results = recommend_trains(
        trains=trains,
        travel_class=request.travel_class,
        passengers=request.passengers,
        preference=request.preference,
        arrival_before=request.arrival_before,
    )

    return results


def explain_recommendation(
    request,
    results,
):

    if not results:
        return "No suitable train was found."

    # IMPORTANT:
    # Python has already selected the train.
    # Ollama is only allowed to explain it.

    selected = results[0]

    prompt = f"""
You are explaining a railway recommendation.

The application has ALREADY selected this exact train:

Train Number: {selected.train_number}
Train Name: {selected.train_name}
Departure: {selected.departure}
Arrival: {selected.arrival}
Duration: {selected.duration}
Class: {selected.travel_class}
Availability: {selected.availability}
Fare per passenger: ₹{selected.fare_per_passenger}
Passengers: {request.passengers}
Total fare: ₹{selected.total_fare}

User preference:
{request.preference}

DO NOT change the selected train.

DO NOT recommend another train.

DO NOT change the fare.

DO NOT change availability.

DO NOT invent information.

Explain briefly why this exact train was selected.
"""

    try:

        response = ollama.chat(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You explain application decisions. "
                        "Never change application data."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        return response["message"]["content"]

    except Exception:

        return (
            f"{selected.train_number} — "
            f"{selected.train_name} is the highest-ranked "
            f"option based on your selected preferences."
        )