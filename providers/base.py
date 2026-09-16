from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class RailwayDataProvider(ABC):
    """Common interface for demo and future authorized live railway data."""

    @abstractmethod
    def search_trains(
        self,
        origin: str,
        destination: str,
        journey_date: str,
        travel_class: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def check_availability(
        self,
        train_number: str,
        journey_date: str,
        travel_class: str,
    ) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_fare(
        self,
        train_number: str,
        journey_date: str,
        travel_class: str,
    ) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_schedule(
        self,
        train_number: str,
        journey_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_train_status(
        self,
        train_number: str,
        journey_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_pnr_status(self, pnr: str) -> Dict[str, Any]:
        raise NotImplementedError
