from tools.railway_provider import railway_provider

def search_trains_via_provider(origin, destination, journey_date, travel_class=None):
    return railway_provider().search_trains(
        origin=origin,
        destination=destination,
        journey_date=journey_date,
        travel_class=travel_class,
    )
