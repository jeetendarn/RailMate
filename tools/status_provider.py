from tools.railway_provider import railway_provider

def get_train_status_via_provider(train_number, journey_date=None):
    return railway_provider().get_train_status(
        train_number=train_number,
        journey_date=journey_date,
    )

def get_schedule_via_provider(train_number, journey_date=None):
    return railway_provider().get_schedule(
        train_number=train_number,
        journey_date=journey_date,
    )

def get_pnr_status_via_provider(pnr):
    return railway_provider().get_pnr_status(pnr)
