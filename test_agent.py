from agent.tool_agent import RailMateToolAgent
from agent.schemas import TravelRequest


print("=" * 70)
print("🚆 RAILMATE v0.4.1 — CONTROLLED TOOL AGENT")
print("=" * 70)


request = TravelRequest(
    origin="Mysore",
    destination="Chennai",
    journey_date="2026-09-21",
    passengers=2,
    travel_class="2A",
    preference="evening",
)


agent = RailMateToolAgent()


result = agent.run(
    """
    Find the best train for my journey.
    Use the railway tools to search, check availability
    and recommend the most suitable train.
    """,

    request,
)


print("\n")
print("=" * 70)
print("🤖 FINAL AGENT RESPONSE")
print("=" * 70)

print(result)


print("\n")
print("=" * 70)
print("📊 PYTHON FINAL RECOMMENDATION")
print("=" * 70)


if agent.last_recommendations:

    best = agent.last_recommendations[0]

    print(
        f"Train: {best.train_number} — "
        f"{best.train_name}"
    )

    print(
        f"Departure: {best.departure}"
    )

    print(
        f"Arrival: {best.arrival}"
    )

    print(
        f"Class: {best.travel_class}"
    )

    print(
        f"Availability: {best.availability}"
    )

    print(
        f"Fare: ₹{best.fare_per_passenger}"
    )

    print(
        f"Passengers: {request.passengers}"
    )

    print(
        f"Total: ₹{best.total_fare}"
    )

    print(
        f"Score: {best.score}"
    )

else:

    print(
        "No Python recommendation was generated."
    )