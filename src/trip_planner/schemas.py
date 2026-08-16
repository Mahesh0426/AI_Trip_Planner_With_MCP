from pydantic import BaseModel, Field
from typing import Literal

# ---------- TripConstraints ----------
class TripConstraints(BaseModel):
    destination: str = ""
    origin: str = ""
    duration: str = ""
    budget: str = ""
    travel_style: str = ""
    special_preferences: list[str] = Field(default_factory=list)


# ---------- SupervisorDecision ----------
class SupervisorDecision(BaseModel):
    selected_agents: list[
        Literal[
            "flight_agent",
            "hotel_agent",
            "weather_agent",
            "budget_agent",
            "itinerary_agent",
        ]
    ]
    trip_constraints: TripConstraints
    reasoning: str