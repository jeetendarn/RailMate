"""RailMate v0.7 DEMO train operational status and route data."""

DEMO_STATUS = {
    "16221": {"status": "RUNNING", "delay_minutes": 10, "expected_departure": "21:25", "expected_arrival": "07:20", "platform": "4"},
    "12610": {"status": "ON TIME", "delay_minutes": 0, "expected_departure": "18:30", "expected_arrival": "05:45", "platform": "2"},
    "22638": {"status": "DELAYED", "delay_minutes": 25, "expected_departure": "16:25", "expected_arrival": "03:55", "platform": "6"},
    "12675": {"status": "ON TIME", "delay_minutes": 0, "expected_departure": "06:15", "expected_arrival": "17:00", "platform": "1"},
    "12007": {"status": "ON TIME", "delay_minutes": 0, "expected_departure": "05:30", "expected_arrival": "14:45", "platform": "3"},
}

DEMO_ROUTES = {
    "16221": ["Mysuru", "Mandya", "Channapatna", "Kengeri", "KSR Bengaluru", "Krishnarajapuram", "Bangarapet", "Jolarpettai", "Katpadi", "Arakkonam", "Chennai"],
    "12610": ["Mysuru", "Mandya", "Maddur", "Kengeri", "KSR Bengaluru", "Bangarapet", "Jolarpettai", "Katpadi", "Chennai"],
    "22638": ["Mysuru", "Mandya", "KSR Bengaluru", "Hosur", "Salem", "Erode", "Tiruppur", "Coimbatore", "Palakkad", "Shoranur", "Thrissur", "Ernakulam", "Alappuzha", "Kottayam", "Chennai"],
    "12675": ["Mysuru", "Mandya", "KSR Bengaluru", "Bangarapet", "Salem", "Erode", "Tiruppur", "Coimbatore", "Erode", "Salem", "Chennai"],
    "12007": ["Mysuru", "Mandya", "KSR Bengaluru", "Bangarapet", "Jolarpettai", "Katpadi", "Chennai"],
}

def get_train_status(train_number: str):
    number = str(train_number).strip()
    data = DEMO_STATUS.get(number)
    if not data:
        return {"success": False, "message": f"No DEMO status data found for train {number}."}
    return {"success": True, "demo": True, "train_number": number, **data}

def get_train_route(train_number: str):
    number = str(train_number).strip()
    stops = DEMO_ROUTES.get(number)
    if not stops:
        return {"success": False, "message": f"No DEMO route data found for train {number}."}
    return {"success": True, "demo": True, "train_number": number, "stops": stops, "stop_count": len(stops)}
