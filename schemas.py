from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from models import IncidentStatus, IncidentSource

class IncidentBase(BaseModel):
    description: str
    source: IncidentSource

class IncidentCreate(IncidentBase):
    pass

class IncidentUpdate(BaseModel):
    status: IncidentStatus

class IncidentResponse(IncidentBase):
    id: int
    status: IncidentStatus
    created_at: datetime
    
    class Config:
        from_attributes = True