from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"


class PipelineOut(BaseModel):
    id: int
    name: str
    length_m: float
    diameter_m: float
    content_type: str

    model_config = {"from_attributes": True}


class SensorReadingOut(BaseModel):
    id: int
    ts: datetime
    pressure_in: float
    pressure_out: float
    flow_in: float
    flow_out: float
    temperature: float

    model_config = {"from_attributes": True}


class DetectionOut(BaseModel):
    id: int
    ts: datetime
    method: str
    leak_suspected: bool
    severity: str
    metrics: Dict[str, Any] = Field(default_factory=dict)

    model_config = {"from_attributes": True}


class MethodStatus(BaseModel):
    method: str
    leak_suspected: bool
    severity: str
    metrics: Dict[str, Any] = Field(default_factory=dict)


class StatusResponse(BaseModel):
    transport_status: str
    monitor_status: str
    content_type: str
    latest: Optional[SensorReadingOut] = None
    flow_change_rate: Optional[float] = None
    pressure_change_rate: Optional[float] = None
    methods: List[MethodStatus] = Field(default_factory=list)
    leak_injected: bool
    transport_running: bool


class SimToggleRequest(BaseModel):
    enabled: bool


class TransportToggleRequest(BaseModel):
    running: bool


class SimStateOut(BaseModel):
    leak_injected: bool
    transport_running: bool
