from typing import Optional, List
from pydantic import BaseModel, Field


class TravelRequest(BaseModel):
    origin: Optional[str] = None
    destination: Optional[str] = None
    journey_date: Optional[str] = None
    passengers: Optional[int] = None
    travel_class: Optional[str] = None
    departure_time: Optional[str] = None
    arrival_before: Optional[str] = None
    preference: Optional[str] = None


class Train(BaseModel):
    train_number: str
    train_name: str
    origin: str
    destination: str
    departure: str
    arrival: str
    duration: str
    running_days: List[str]
    availability: dict
    fares: dict
    stops: int


class TrainOption(BaseModel):
    train_number: str
    train_name: str
    departure: str
    arrival: str
    duration: str
    travel_class: str
    availability: str
    fare_per_passenger: Optional[float] = None
    total_fare: Optional[float] = None
    score: int


class AgentState(BaseModel):
    travel_request: TravelRequest = Field(default_factory=TravelRequest)

    selected_train: Optional[str] = None
    selected_option: Optional[TrainOption] = None

    search_completed: bool = False
    awaiting_selection: bool = False
    awaiting_confirmation: bool = False
    booking_started: bool = False