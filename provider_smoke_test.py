from providers.factory import get_railway_provider

provider = get_railway_provider()
print("Provider:", type(provider).__name__)

results = provider.search_trains(
    origin="Mysore",
    destination="Chennai",
    journey_date="2026-09-21",
    travel_class="2A",
)

print("Search results:", len(results))
if results:
    first = results[0]
    print("First train:", first.get("train_number", first.get("number")))
    print("Data source:", first.get("data_source"))
    print("Live:", first.get("live"))

print("Provider smoke test completed.")
