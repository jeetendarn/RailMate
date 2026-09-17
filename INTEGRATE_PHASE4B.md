# RailMate Phase 4B — Integration

Add these files to the existing RailMate project.

First run the provider smoke test. We are intentionally NOT replacing the
working train-search/recommendation/UI files yet.

From:
C:\Users\jeete\OneDrive\Desktop\RailMate

run:

```powershell
$env:RAILWAY_DATA_MODE="demo"
$env:RAILWAY_PROVIDER="demo"
python provider_smoke_test.py
```

Expected:

```text
Provider: DemoRailwayProvider
Search results: ...
First train: ...
Data source: DEMO
Live: False
Provider smoke test completed.
```

After this passes, migrate the existing railway tools one by one:
1. train search
2. availability/fare
3. status/PNR
4. deterministic recommendation/filtering
5. visible DEMO/LIVE source indicator

Do not implement guessed live API endpoints.
