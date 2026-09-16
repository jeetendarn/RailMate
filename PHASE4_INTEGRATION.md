# RailMate Phase 4 — Railway Data Provider Layer

## Goal

Separate RailMate's AI/recommendation logic from the railway data source.

RailMate can therefore run with:

- `demo` — current `data/trains.json`
- `live` — future authorized railway information provider

## 1. Copy the folder

Copy `providers/` into:

`C:\Users\jeete\OneDrive\Desktop\RailMate\providers\`

Copy `.env.example` to:

`C:\Users\jeete\OneDrive\Desktop\RailMate\.env.example`

Do NOT put API keys in `.env.example`.

## 2. Keep demo mode first

In PowerShell:

```powershell
$env:RAILWAY_DATA_MODE="demo"
$env:RAILWAY_PROVIDER="demo"
```

Then run the existing RailMate application exactly as before.

## 3. Next integration point

The next change in the existing application should be to replace direct reads/imports of demo railway data with:

```python
from providers.factory import get_railway_provider

provider = get_railway_provider()
```

Then use:

```python
provider.search_trains(...)
provider.check_availability(...)
provider.get_fare(...)
provider.get_schedule(...)
provider.get_train_status(...)
provider.get_pnr_status(...)
```

The existing recommendation engine remains authoritative for sorting/filtering.

## 4. Live mode

Do NOT set live mode until an authorized provider has supplied:

- API base URL
- authentication method
- request/response documentation
- station-code rules
- availability/fare contract
- PNR/status contract
- rate limits
- commercial/usage permissions

Then we implement that provider-specific adapter.

## 5. Booking boundary

RailMate will NOT store or process:

- IRCTC password
- CAPTCHA
- OTP
- card number
- CVV
- UPI PIN
- payment credentials

Final login, payment and booking remain on the official railway booking service.

## 6. Important data rule

Until the live adapter is implemented, every result must remain visibly marked:

`DEMO DATA — NOT LIVE RAILWAY AVAILABILITY`

Never convert demo values into claims of live availability.
