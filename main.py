from agent.agent import (
    extract_request,
    missing_information,
    generate_question,
)

from agent.schemas import TravelRequest
from agent.tool_agent import RailMateToolAgent

from tools.recommendation import (
    find_cheapest,
    find_fastest,
    find_earliest,
    find_latest,
    filter_confirmed,
    filter_after_time,
    filter_before_arrival,
    compare_trains,
)


STATE_COLLECTING = "collecting"
STATE_RESULTS = "results"
STATE_REVIEW = "review"


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


def print_options(options, title="🚆 RAILMATE AI — TRAIN OPTIONS"):

    print("\n")
    print("=" * 70)
    print(title)
    print("=" * 70)

    print("\n⚠ DEMO MODE — SAMPLE RAILWAY DATA")
    print("Live railway availability is not connected yet.\n")

    if not options:
        print("No matching trains found.")
        return

    for index, option in enumerate(options, 1):

        print(
            f"{index}. {option['train_number']} — "
            f"{option['train_name']}"
        )

        print(
            f"   {option['departure']} → "
            f"{option['arrival']}"
        )

        print(
            f"   Duration: {option['duration']}"
        )

        print(
            f"   {option['travel_class']}: "
            f"{option['availability']}"
        )

        print(
            f"   Fare: ₹{option['fare_per_passenger']} "
            f"per passenger"
        )

        print(
            f"   Total for "
            f"{option.get('total_fare', 0) / option['fare_per_passenger']:.0f}: "
            f"₹{option['total_fare']}"
        )

        print(
            f"   Agent Score: {option['score']}"
        )

        print()


def print_single_option(option, heading):

    if not option:
        print("\n❌ No matching train found.")
        return

    print("\n" + "=" * 70)
    print(heading)
    print("=" * 70)

    print(
        f"\n🚆 {option['train_number']} — "
        f"{option['train_name']}"
    )

    print(
        f"Departure: {option['departure']}"
    )

    print(
        f"Arrival:   {option['arrival']}"
    )

    print(
        f"Duration:  {option['duration']}"
    )

    print(
        f"Class:     {option['travel_class']}"
    )

    print(
        f"Status:    {option['availability']}"
    )

    print(
        f"Fare:      ₹{option['fare_per_passenger']} "
        f"per passenger"
    )

    print(
        f"Total:     ₹{option['total_fare']}"
    )


def print_recommendation(option, explanation):

    if not option:
        return

    print("\n")
    print("=" * 70)
    print("🤖 RAILMATE RECOMMENDATION")
    print("=" * 70)

    print(
        f"\nRecommended: "
        f"{option['train_number']} — "
        f"{option['train_name']}"
    )

    print(
        f"Departure: {option['departure']}"
    )

    print(
        f"Arrival: {option['arrival']}"
    )

    print(
        f"Duration: {option['duration']}"
    )

    print(
        f"Class: {option['travel_class']}"
    )

    print(
        f"Availability: {option['availability']}"
    )

    print(
        f"Fare: ₹{option['fare_per_passenger']} "
        f"per passenger"
    )

    print(
        f"Passengers: "
        f"{int(option['total_fare'] / option['fare_per_passenger'])}"
    )

    print(
        f"Estimated total: ₹{option['total_fare']}"
    )

    print("\nWhy this train?")

    print(explanation)


def print_booking_review(request, option):

    print("\n")
    print("=" * 70)
    print("🎫 BOOKING REVIEW")
    print("=" * 70)

    print("\n⚠ DEMO MODE")

    print(
        f"\nTrain: {option['train_number']} — "
        f"{option['train_name']}"
    )

    print(
        f"Journey: {request.origin} → "
        f"{request.destination}"
    )

    print(
        f"Date: {request.journey_date}"
    )

    print(
        f"Departure: {option['departure']}"
    )

    print(
        f"Arrival: {option['arrival']}"
    )

    print(
        f"Duration: {option['duration']}"
    )

    print(
        f"Class: {option['travel_class']}"
    )

    print(
        f"Availability: {option['availability']}"
    )

    print(
        f"Passengers: {request.passengers}"
    )

    print(
        f"Fare per passenger: "
        f"₹{option['fare_per_passenger']}"
    )

    print(
        f"Estimated total fare: "
        f"₹{option['total_fare']}"
    )

    print("\n" + "-" * 40)

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


def booking_handoff():

    print("\n")
    print("=" * 70)
    print("🔐 SECURE BOOKING HANDOFF")
    print("=" * 70)

    print(
        "\nRailMate is ready to hand off the "
        "booking to an authorized railway provider."
    )

    print(
        "\nRailMate does NOT collect or store:"
    )

    print("• Railway password")
    print("• OTP")
    print("• CAPTCHA")
    print("• Card number")
    print("• CVV")
    print("• UPI PIN")

    print(
        "\nIn the live version, the authorized "
        "provider will handle authentication "
        "and payment."
    )

    print(
        "\n🚧 LIVE BOOKING PROVIDER INTEGRATION "
        "WILL BE ADDED IN A FUTURE VERSION."
    )


def normalize_text(text):

    return text.strip().lower()


def main():

    print("=" * 70)
    print("🤖 RAILMATE AI AGENT v0.6")
    print("=" * 70)

    print("\nPowered by Ollama + Llama 3.2")
    print("Local AI — No API key required")

    print("\n⚠ Railway information is currently DEMO data.")

    print("\nType 'exit' to quit.")
    print("💡 You can speak naturally with RailMate.")

    state = STATE_COLLECTING

    request = TravelRequest()

    selected_option = None

    agent = RailMateToolAgent()

    while True:

        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nRailMate: Goodbye! 🚆")
            break

        if not user_input:
            continue

        if normalize_text(user_input) == "exit":

            print("\nRailMate: Goodbye! 🚆")
            break

        # ======================================================
        # COLLECTING TRAVEL INFORMATION
        # ======================================================

        if state == STATE_COLLECTING:

            new_request = extract_request(
                user_input,
                existing_request=request
            )

            request = new_request

            print_request(request)

            missing = missing_information(request)

            if missing:

                question = generate_question(
                    missing[0]
                )

                print(
                    f"\nRailMate: {question}"
                )

                continue

            print(
                "\n🤖 RailMate Agent is planning "
                "your railway search..."
            )

            options = agent.run(
                user_input,
                request
            )

            if not options:

                print(
                    "\nRailMate: I couldn't find "
                    "a suitable train."
                )

                continue

            print_options(options)

            best = options[0]

            explanation = agent.explain(best)

            print_recommendation(
                best,
                explanation
            )

            print("\nWhat would you like to do?")

            print("1. Select recommended train")
            print("2. See all train options")
            print("3. Change preferences")
            print("4. Start a new search")

            print(
                "\nYou can also ask naturally:"
            )

            print('• "Show me the cheapest"')
            print('• "Show me the fastest"')
            print('• "Show only confirmed seats"')
            print('• "Show trains after 6 PM"')
            print('• "I need to arrive before 6 AM"')
            print('• "Compare 16221 and 12610"')
            print('• "Why did you choose this train?"')

            state = STATE_RESULTS

            continue

        # ======================================================
        # RESULTS / FOLLOW-UP REASONING
        # ======================================================

        if state == STATE_RESULTS:

            text = normalize_text(user_input)

            options = agent.last_recommendations

            # --------------------------------------------------
            # RECOMMENDED TRAIN
            # --------------------------------------------------

            if (
                text in {
                    "1",
                    "select",
                    "select recommended",
                    "book recommended",
                    "select recommended train",
                    "book recommended train",
                }
            ):

                selected_option = options[0]

                print_booking_review(
                    request,
                    selected_option
                )

                state = STATE_REVIEW
                continue

            # --------------------------------------------------
            # SHOW ALL
            # --------------------------------------------------

            if text in {
                "2",
                "show all",
                "show all options",
                "all trains",
                "show trains",
            }:

                print_options(options)

                continue

            # --------------------------------------------------
            # CHANGE PREFERENCES
            # --------------------------------------------------

            if text in {
                "3",
                "change",
                "change preferences",
            }:

                print(
                    "\nRailMate: Tell me what you "
                    "would like to change."
                )

                state = STATE_COLLECTING

                continue

            # --------------------------------------------------
            # NEW SEARCH
            # --------------------------------------------------

            if text in {
                "4",
                "new search",
                "start a new search",
            }:

                request = TravelRequest()
                selected_option = None

                state = STATE_COLLECTING

                print(
                    "\nRailMate: Sure. "
                    "Where would you like to travel?"
                )

                continue

            # --------------------------------------------------
            # CHEAPEST
            # --------------------------------------------------

            if "cheap" in text or "lowest fare" in text:

                result = find_cheapest(options)

                print_single_option(
                    result,
                    "💰 CHEAPEST TRAIN"
                )

                continue

            # --------------------------------------------------
            # FASTEST
            # --------------------------------------------------

            if "fastest" in text or "shortest" in text:

                result = find_fastest(options)

                print_single_option(
                    result,
                    "⚡ FASTEST TRAIN"
                )

                continue

            # --------------------------------------------------
            # EARLIEST
            # --------------------------------------------------

            if "earliest" in text:

                result = find_earliest(options)

                print_single_option(
                    result,
                    "🌅 EARLIEST DEPARTURE"
                )

                continue

            # --------------------------------------------------
            # LATEST
            # --------------------------------------------------

            if "latest" in text:

                result = find_latest(options)

                print_single_option(
                    result,
                    "🌙 LATEST DEPARTURE"
                )

                continue

            # --------------------------------------------------
            # CONFIRMED ONLY
            # --------------------------------------------------

            if (
                "confirmed" in text
                or "confirmed seats" in text
                or "only available" in text
            ):

                result = filter_confirmed(options)

                print_options(
                    result,
                    "🎫 CONFIRMED AVAILABILITY"
                )

                continue

            # --------------------------------------------------
            # AFTER TIME
            # --------------------------------------------------

            if "after 6 pm" in text or "after 6pm" in text:

                result = filter_after_time(
                    options,
                    "18:00"
                )

                print_options(
                    result,
                    "🕕 TRAINS AFTER 6 PM"
                )

                continue

            if "after 5 pm" in text or "after 5pm" in text:

                result = filter_after_time(
                    options,
                    "17:00"
                )

                print_options(
                    result,
                    "🕔 TRAINS AFTER 5 PM"
                )

                continue

            if "after 7 pm" in text or "after 7pm" in text:

                result = filter_after_time(
                    options,
                    "19:00"
                )

                print_options(
                    result,
                    "🕖 TRAINS AFTER 7 PM"
                )

                continue

            # --------------------------------------------------
            # ARRIVAL BEFORE
            # --------------------------------------------------

            if "before 6 am" in text or "before 6am" in text:

                result = filter_before_arrival(
                    options,
                    "06:00"
                )

                print_options(
                    result,
                    "⏰ TRAINS ARRIVING BEFORE 6 AM"
                )

                continue

            # --------------------------------------------------
            # WHY
            # --------------------------------------------------

            if (
                "why" in text
                or "why this train" in text
                or "why did you choose" in text
            ):

                explanation = agent.explain(
                    options[0]
                )

                print(
                    "\n🤖 RailMate:"
                )

                print(explanation)

                continue

            # --------------------------------------------------
            # COMPARE
            # --------------------------------------------------

            if "compare" in text:

                numbers = []

                for option in options:

                    if option["train_number"] in user_input:

                        numbers.append(
                            option["train_number"]
                        )

                if len(numbers) >= 2:

                    comparison = compare_trains(
                        options,
                        numbers
                    )

                    print_options(
                        comparison,
                        "⚖ TRAIN COMPARISON"
                    )

                else:

                    print(
                        "\nRailMate: Please tell me "
                        "the train numbers you want "
                        "to compare."
                    )

                    print(
                        'Example: "Compare 16221 and 12610"'
                    )

                continue

            # --------------------------------------------------
            # DIRECT TRAIN SELECTION
            # --------------------------------------------------

            found = None

            for option in options:

                if option["train_number"] in user_input:

                    found = option
                    break

            if found:

                selected_option = found

                print_booking_review(
                    request,
                    selected_option
                )

                state = STATE_REVIEW

                continue

            # --------------------------------------------------
            # 3A / CLASS CHANGE
            # --------------------------------------------------

            if "3a" in text:

                request.travel_class = "3A"

                print(
                    "\nRailMate: Switching to 3A "
                    "and recalculating options..."
                )

                options = agent.run(
                    "Change travel class to 3A",
                    request
                )

                print_options(options)

                print_recommendation(
                    options[0],
                    agent.explain(options[0])
                )

                continue

            # --------------------------------------------------
            # 2A
            # --------------------------------------------------

            if "2a" in text:

                request.travel_class = "2A"

                print(
                    "\nRailMate: Switching to 2A "
                    "and recalculating options..."
                )

                options = agent.run(
                    "Change travel class to 2A",
                    request
                )

                print_options(options)

                continue

            # --------------------------------------------------
            # UNKNOWN FOLLOW-UP
            # --------------------------------------------------

            print(
                "\nRailMate: I can help with:"
            )

            print(
                "• cheapest"
            )

            print(
                "• fastest"
            )

            print(
                "• confirmed seats"
            )

            print(
                "• departure time"
            )

            print(
                "• arrival deadline"
            )

            print(
                "• train comparison"
            )

            print(
                "• class changes"
            )

            print(
                "• train selection"
            )

            continue

        # ======================================================
        # BOOKING REVIEW
        # ======================================================

        if state == STATE_REVIEW:

            text = normalize_text(user_input)

            if text in {
                "1",
                "yes",
                "confirm",
                "continue",
                "proceed",
                "book",
                "continue booking",
            }:

                booking_handoff()

                state = STATE_RESULTS

                print(
                    "\nRailMate: You are back at "
                    "the train results."
                )

                continue

            if text in {
                "2",
                "back",
                "go back",
                "cancel",
            }:

                print_options(
                    agent.last_recommendations
                )

                state = STATE_RESULTS

                continue

            print(
                "\nPlease choose:"
            )

            print("1. Continue")
            print("2. Go back")


if __name__ == "__main__":
    main()