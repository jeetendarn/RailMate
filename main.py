from agent.agent import (
    extract_request,
    missing_information,
    generate_question,
)

from agent.schemas import TravelRequest

from agent.tool_agent import RailMateToolAgent


STATE_COLLECTING = "COLLECTING"
STATE_RESULTS = "RESULTS"
STATE_BOOKING_REVIEW = "BOOKING_REVIEW"


# ==============================================================
# DISPLAY REQUEST
# ==============================================================

def print_request(request):

    print("\n[Agent understood]")

    print(f"From:       {request.origin}")
    print(f"To:         {request.destination}")
    print(f"Date:       {request.journey_date}")
    print(f"Passengers: {request.passengers}")
    print(f"Class:      {request.travel_class}")
    print(f"Time:       {request.departure_time}")
    print(f"Arrival:    {request.arrival_before}")
    print(f"Preference: {request.preference}")


# ==============================================================
# DISPLAY TRAIN OPTIONS
# ==============================================================

def print_train_options(results):

    print("\n")
    print("=" * 70)
    print("🚆 RAILMATE AI — TRAIN OPTIONS")
    print("=" * 70)

    print("\n⚠ DEMO MODE — SAMPLE RAILWAY DATA")
    print("Live railway availability is not connected yet.\n")

    for index, option in enumerate(
        results,
        start=1
    ):

        print(
            f"{index}. "
            f"{option.train_number} — "
            f"{option.train_name}"
        )

        print(
            f"   Mysuru {option.departure} → "
            f"Chennai {option.arrival}"
        )

        print(
            f"   Duration: {option.duration}"
        )

        print(
            f"   {option.travel_class}: "
            f"{option.availability}"
        )

        print(
            f"   Fare: ₹{option.fare_per_passenger} "
            f"per passenger"
        )

        print(
            f"   Total for {option.travel_class}: "
            f"₹{option.total_fare}"
        )

        print(
            f"   Agent Score: {option.score}"
        )

        print()


# ==============================================================
# RECOMMENDATION
# ==============================================================

def print_recommendation(
    request,
    results,
    explanation,
):

    if not results:
        return

    selected = results[0]

    print("\n")
    print("=" * 70)
    print("🤖 RAILMATE RECOMMENDATION")
    print("=" * 70)

    print(
        f"\nRecommended: "
        f"{selected.train_number} — "
        f"{selected.train_name}"
    )

    print(
        f"Departure: {selected.departure}"
    )

    print(
        f"Arrival: {selected.arrival}"
    )

    print(
        f"Duration: {selected.duration}"
    )

    print(
        f"Class: {selected.travel_class}"
    )

    print(
        f"Availability: {selected.availability}"
    )

    print(
        f"Fare: ₹{selected.fare_per_passenger} "
        f"per passenger"
    )

    print(
        f"Passengers: {request.passengers}"
    )

    print(
        f"Estimated total: ₹{selected.total_fare}"
    )

    print("\nWhy this train?")

    print(explanation)

    print("\nWhat would you like to do?")

    print("1. Select recommended train")
    print("2. See all train options")
    print("3. Change preferences")
    print("4. Start a new search")

    print(
        "\nYou can also type a natural request such as:"
    )

    print(
        '• "Select train 16221"'
    )

    print(
        '• "Show me the cheapest"'
    )

    print(
        '• "Show me the fastest"'
    )


# ==============================================================
# FIND TRAIN BY NUMBER
# ==============================================================

def find_train_by_number(
    results,
    train_number,
):

    train_number = str(
        train_number
    ).strip()

    for option in results:

        if str(
            option.train_number
        ) == train_number:

            return option

    return None


# ==============================================================
# SELECT TRAIN
# ==============================================================

def select_train(
    results,
    user_input,
):

    text = user_input.lower().strip()

    # ----------------------------------------------------------
    # Recommended train
    # ----------------------------------------------------------

    if text in [
        "1",
        "select",
        "select recommended",
        "select recommended train",
        "book recommended",
        "book the recommended train",
        "recommended",
    ]:

        return results[0]

    # ----------------------------------------------------------
    # Numeric menu selection
    # ----------------------------------------------------------

    if text.isdigit():

        number = int(text)

        if 1 <= number <= len(results):

            return results[number - 1]

    # ----------------------------------------------------------
    # Train number
    # ----------------------------------------------------------

    words = text.replace(
        "-",
        " "
    ).split()

    for word in words:

        if word.isdigit():

            option = find_train_by_number(
                results,
                word,
            )

            if option:

                return option

    return None


# ==============================================================
# CHEAPEST
# ==============================================================

def cheapest_train(results):

    available = [

        r for r in results

        if r.availability == "AVAILABLE"
    ]

    if not available:
        available = results

    return min(
        available,
        key=lambda x:
            x.fare_per_passenger
            if x.fare_per_passenger is not None
            else 999999999,
    )


# ==============================================================
# FASTEST
# ==============================================================

def duration_minutes(duration):

    try:

        parts = duration.lower().split()

        hours = 0
        minutes = 0

        for part in parts:

            if part.endswith("h"):
                hours = int(
                    part[:-1]
                )

            elif part.endswith("m"):
                minutes = int(
                    part[:-1]
                )

        return (
            hours * 60
            + minutes
        )

    except Exception:

        return 999999


def fastest_train(results):

    return min(
        results,
        key=lambda x:
            duration_minutes(
                x.duration
            ),
    )


# ==============================================================
# BOOKING REVIEW
# ==============================================================

def print_booking_review(
    request,
    selected,
):

    print("\n")
    print("=" * 70)
    print("🎫 BOOKING REVIEW")
    print("=" * 70)

    print("\n⚠ DEMO MODE")

    print(
        f"\nTrain: "
        f"{selected.train_number} — "
        f"{selected.train_name}"
    )

    print(
        f"Journey: "
        f"{request.origin} → "
        f"{request.destination}"
    )

    print(
        f"Date: {request.journey_date}"
    )

    print(
        f"Departure: "
        f"{selected.departure}"
    )

    print(
        f"Arrival: "
        f"{selected.arrival}"
    )

    print(
        f"Duration: "
        f"{selected.duration}"
    )

    print(
        f"Class: "
        f"{selected.travel_class}"
    )

    print(
        f"Availability: "
        f"{selected.availability}"
    )

    print(
        f"Passengers: "
        f"{request.passengers}"
    )

    print(
        f"Fare per passenger: "
        f"₹{selected.fare_per_passenger}"
    )

    print(
        f"Estimated total fare: "
        f"₹{selected.total_fare}"
    )

    print("\n----------------------------------------")

    print(
        "This is a booking review only."
    )

    print(
        "Actual railway booking, login, OTP, "
        "CAPTCHA and payment will be handled "
        "through an authorized booking provider."
    )

    print("\n1. Continue")
    print("2. Go back")


# ==============================================================
# SECURE HANDOFF
# ==============================================================

def print_booking_handoff(
    request,
    selected,
):

    print("\n")
    print("=" * 70)
    print("🔐 SECURE BOOKING HANDOFF")
    print("=" * 70)

    print(
        f"\nSelected train: "
        f"{selected.train_number} — "
        f"{selected.train_name}"
    )

    print(
        f"Journey: "
        f"{request.origin} → "
        f"{request.destination}"
    )

    print(
        f"Date: "
        f"{request.journey_date}"
    )

    print(
        f"Class: "
        f"{request.travel_class}"
    )

    print(
        f"Passengers: "
        f"{request.passengers}"
    )

    print(
        f"Estimated fare: "
        f"₹{selected.total_fare}"
    )

    print("\nRailMate does NOT collect or store:")

    print("• Railway password")
    print("• OTP")
    print("• CAPTCHA")
    print("• Card number")
    print("• CVV")
    print("• UPI PIN")

    print(
        "\nAuthentication and payment must happen "
        "directly with an authorized provider."
    )

    print(
        "\n⚠ Current prototype:"
    )

    print(
        "Booking handoff is simulated."
    )


# ==============================================================
# MAIN
# ==============================================================

def main():

    request = TravelRequest()

    results = []

    selected_train = None

    state = STATE_COLLECTING

    # Create ONE agent for the session
    tool_agent = RailMateToolAgent()

    print("=" * 70)
    print("🤖 RAILMATE AI AGENT v0.5")
    print("=" * 70)

    print(
        "\nPowered by Ollama + Llama 3.2"
    )

    print(
        "Local AI — No API key required"
    )

    print(
        "\n⚠ Railway information is currently DEMO data."
    )

    print(
        "\nType 'exit' to quit."
    )

    print(
        "\n💡 You can speak naturally with RailMate."
    )

    while True:

        try:

            user_input = input(
                "\nYou: "
            ).strip()

        except KeyboardInterrupt:

            print(
                "\n\nRailMate: Goodbye! 🚆"
            )

            break

        if not user_input:
            continue

        # ======================================================
        # EXIT
        # ======================================================

        if user_input.lower() in [
            "exit",
            "quit",
        ]:

            print(
                "\nRailMate: Goodbye! 🚆"
            )

            break

        # ======================================================
        # BOOKING REVIEW
        # ======================================================

        if state == STATE_BOOKING_REVIEW:

            text = user_input.lower()

            if text in [
                "1",
                "yes",
                "confirm",
                "continue",
                "proceed",
                "book",
            ]:

                print_booking_handoff(
                    request,
                    selected_train,
                )

                print(
                    "\nRailMate: "
                    "Booking workflow completed "
                    "for this prototype."
                )

                print(
                    "\nYou can start another search "
                    "or type 'exit'."
                )

                state = STATE_COLLECTING

                continue

            elif text in [
                "2",
                "back",
                "go back",
            ]:

                state = STATE_RESULTS

                print_train_options(
                    results
                )

                print_recommendation(
                    request,
                    results,
                    "The recommendation remains unchanged."
                )

                continue

            else:

                print(
                    "\nPlease enter 1 to continue "
                    "or 2 to go back."
                )

                continue

        # ======================================================
        # RESULTS STATE
        # ======================================================

        if state == STATE_RESULTS:

            text = user_input.lower().strip()

            # --------------------------------------------------
            # SHOW OPTIONS
            # --------------------------------------------------

            if text in [
                "2",
                "show",
                "show options",
                "show all",
                "show trains",
                "options",
            ]:

                print_train_options(
                    results
                )

                print_recommendation(
                    request,
                    results,
                    "These are the current ranked options."
                )

                continue

            # --------------------------------------------------
            # CHANGE PREFERENCES
            # --------------------------------------------------

            if text in [
                "3",
                "change",
                "change preferences",
                "modify",
                "modify preferences",
            ]:

                state = STATE_COLLECTING

                print(
                    "\nRailMate: "
                    "Tell me what you would like to change."
                )

                print(
                    "For example:"
                )

                print(
                    "• Make it 3A"
                )

                print(
                    "• I want morning trains"
                )

                print(
                    "• Change passengers to 3"
                )

                continue

            # --------------------------------------------------
            # NEW SEARCH
            # --------------------------------------------------

            if text in [
                "4",
                "new",
                "new search",
                "start new search",
                "restart",
            ]:

                request = TravelRequest()

                results = []

                selected_train = None

                state = STATE_COLLECTING

                tool_agent = RailMateToolAgent()

                print(
                    "\n🔄 Starting a new journey search."
                )

                continue

            # --------------------------------------------------
            # SELECT TRAIN
            # --------------------------------------------------

            selected = select_train(
                results,
                user_input,
            )

            # Cheapest
            if selected is None and (
                "cheapest" in text
                or "lowest fare" in text
                or "least expensive" in text
            ):

                selected = cheapest_train(
                    results
                )

                print(
                    f"\n💰 Cheapest available option: "
                    f"{selected.train_number}"
                )

            # Fastest
            if selected is None and (
                "fastest" in text
                or "quickest" in text
                or "shortest" in text
            ):

                selected = fastest_train(
                    results
                )

                print(
                    f"\n⚡ Fastest option: "
                    f"{selected.train_number}"
                )

            # --------------------------------------------------
            # TRAIN SELECTED
            # --------------------------------------------------

            if selected:

                selected_train = selected

                print_booking_review(
                    request,
                    selected_train,
                )

                state = STATE_BOOKING_REVIEW

                continue

            print(
                "\nRailMate: "
                "I couldn't identify that train choice."
            )

            print(
                "Try:"
            )

            print(
                "1"
            )

            print(
                "train number such as 16221"
            )

            print(
                '"show cheapest"'
            )

            print(
                '"show fastest"'
            )

            print(
                '"change preferences"'
            )

            continue

        # ======================================================
        # COLLECTING STATE
        # ======================================================

        request = extract_request(
            user_input,
            request,
        )

        print_request(
            request
        )

        missing = missing_information(
            request
        )

        # ======================================================
        # MISSING INFORMATION
        # ======================================================

        if missing:

            question = generate_question(
                missing
            )

            print(
                f"\nRailMate: {question}"
            )

            continue

        # ======================================================
        # COMPLETE REQUEST
        # ======================================================

        print(
            "\n🤖 RailMate Agent is planning "
            "your railway search..."
        )

        # ======================================================
        # TRUE TOOL AGENT
        # ======================================================

        explanation = tool_agent.run(

            """
Use the railway tools to search the route,
verify the requested class and determine
the best available train according to
the user's preferences.

The application will display the final
ranked railway options.
""",

            request,
        )

        results = (
            tool_agent.last_recommendations
        )

        # ======================================================
        # NO RESULTS
        # ======================================================

        if not results:

            print(
                "\nRailMate: "
                "No suitable demo trains were found."
            )

            print(
                "\nYou can change your route, "
                "class or travel preferences."
            )

            continue

        # ======================================================
        # DISPLAY RESULTS
        # ======================================================

        print_train_options(
            results
        )

        print_recommendation(
            request,
            results,
            explanation,
        )

        state = STATE_RESULTS


# ==============================================================
# START
# ==============================================================

if __name__ == "__main__":
    main()