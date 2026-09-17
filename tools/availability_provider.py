from tools.railway_provider import railway_provider

def check_availability_via_provider(train_number, journey_date, travel_class):
    return railway_provider().check_availability(
        train_number=train_number,
        journey_date=journey_date,
        travel_class=travel_class,
    )

def get_fare_via_provider(train_number, journey_date, travel_class):
    return railway_provider().get_fare(
        train_number=train_number,
        journey_date=journey_date,
        travel_class=travel_class,
    )
