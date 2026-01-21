from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

class UserBase(BaseModel):
    username: str
    role: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    class Config:
        from_attributes = True

class TemplateCreate(BaseModel):
    name: str
    graph_json: Any

class TemplateResponse(TemplateCreate):
    id: int
    version: int
    created_at: datetime
    class Config:
        from_attributes = True

class ExecutionResponse(BaseModel):
    id: int
    node_id: str
    status: str
    predicted_duration: Optional[int]
    actual_duration: Optional[int]
    start_time: datetime
    end_time: Optional[datetime]
    executed_by: Optional[int]
    class Config:
        from_attributes = True

class InstanceCreate(BaseModel):
    template_id: int

class InstanceResponse(BaseModel):
    id: int
    template_id: int
    status: str
    current_node_id: Optional[str]
    executions: List[ExecutionResponse] = []
    class Config:
        from_attributes = True
