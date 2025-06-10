# schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# ---- Sensor ----
class SensorBase(BaseModel):
    type: str
    pin: str
    status: Optional[str] = "enabled"

class SensorCreate(SensorBase):
    pass

class Sensor(SensorBase):
    id: int
    node_id: int

    class Config:
        orm_mode = True

# ---- Node ----
class NodeBase(BaseModel):
    ip: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    sensor_count: Optional[int] = 0

class NodeCreate(NodeBase):
    pass

class Node(NodeBase):
    id: int
    hub_id: int
    sensors: List[Sensor] = []

    class Config:
        orm_mode = True

# ---- Hub ----
class HubBase(BaseModel):
    name: str
    ip: str
    last_seen: Optional[datetime] = None

class HubCreate(HubBase):
    pass

class Hub(HubBase):
    id: int
    nodes: List[Node] = []

    class Config:
        orm_mode = True

# ---- Users ----
class UserBase(BaseModel):
    username: str
    email: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

# ---- Token ----
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
