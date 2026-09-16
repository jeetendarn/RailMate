import os
from typing import Any, Dict, List, Optional

from .base import RailwayDataProvider


class LiveProviderNotConfigured(RuntimeError):
    """Raised until an authorized live railway provider is configured."""


class LiveRailwayProvider(RailwayDataProvider):
    """
    Safe placeholder for an authorized railway information provider.

    IMPORTANT:
    No unofficial endpoint, scraping, CAPTCHA bypass, IRCTC password,
    OTP, payment data, or invented API contract is implemented here.
    Configure this only after obtaining an authorized provider/API contract.
    """

    def __init__(self):
        self.base_url = os.getenv("LIVE_PROVIDER_BASE_URL", "").strip()
        self.api_key = os.getenv("LIVE_PROVIDER_API_KEY", "").strip()

    def _raise(self):
        if not self.base_url or not self.api_key:
            raise LiveProviderNotConfigured(
                "LIVE PROVIDER NOT CONFIGURED. "
                "Set LIVE_PROVIDER_BASE_URL and LIVE_PROVIDER_API_KEY "
                "after obtaining an authorized railway data API."
            )
        raise LiveProviderNotConfigured(
            "Live provider credentials are present, but the provider-specific "
            "API contract has not been implemented. Do not guess endpoints."
        )

    def search_trains(self, origin, destination, journey_date, travel_class=None):
        self._raise()

    def check_availability(self, train_number, journey_date, travel_class):
        self._raise()

    def get_fare(self, train_number, journey_date, travel_class):
        self._raise()

    def get_schedule(self, train_number, journey_date=None):
        self._raise()

    def get_train_status(self, train_number, journey_date=None):
        self._raise()

    def get_pnr_status(self, pnr):
        self._raise()
