import os

from .demo_provider import DemoRailwayProvider
from .live_provider import LiveRailwayProvider
from .base import RailwayDataProvider


def get_railway_provider() -> RailwayDataProvider:
    mode = os.getenv("RAILWAY_DATA_MODE", "demo").strip().lower()
    provider_name = os.getenv("RAILWAY_PROVIDER", mode).strip().lower()

    if mode == "live" or provider_name == "live":
        return LiveRailwayProvider()

    return DemoRailwayProvider()
