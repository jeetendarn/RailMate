"""RailMate v0.7 DEMO PNR status. Never use real credentials or live PNR data here."""

DEMO_PNRS = {
    "1234567890": {"train_number": "16221", "passengers": 2, "status": "CONFIRMED", "coach": "A1", "berths": ["32", "33"]},
    "9876543210": {"train_number": "12610", "passengers": 1, "status": "RAC", "coach": "B2", "berths": ["18"]},
}

def get_pnr_status(pnr: str):
    value = str(pnr).strip()
    if not value.isdigit() or len(value) != 10:
        return {"success": False, "message": "Please provide a 10-digit DEMO PNR number."}
    data = DEMO_PNRS.get(value)
    if not data:
        return {"success": False, "demo": True, "pnr": value, "message": "PNR not found in the DEMO dataset."}
    return {"success": True, "demo": True, "pnr": value, **data}
