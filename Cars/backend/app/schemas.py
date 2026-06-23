from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class CarSpecs(BaseModel):
    horsepower: int
    torque: str
    acceleration: str
    topSpeed: str
    rangeOrMileage: str
    batteryCapacity: Optional[str] = None
    engine: str
    seating: int
    cargoVolume: str

class Car(BaseModel):
    id: str
    brand: str
    model: str
    year: int
    price: float
    bodyType: str
    fuelType: str
    transmission: str
    drivetrain: str
    specs: CarSpecs
    features: List[str]
    description: str

class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class CompareRequest(BaseModel):
    cars: List[Car]
    user_query: Optional[str] = None
    mode: Literal["automatic", "manual"] = "automatic"
    chat_history: Optional[List[Message]] = None
    summary: Optional[str] = None

class CompareResponse(BaseModel):
    thread_id: str
    mode: str
    analysis: Optional[str] = None
    requires_review: bool = False
    hitl_approved: bool = False
    iterations: int = 0
    feedback_needed: Optional[str] = None
    chat_history: List[Message] = Field(default_factory=list)
    summary: Optional[str] = None

class ReviewRequest(BaseModel):
    approved: bool
    feedback: Optional[str] = None

