from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base

class Hub(Base):
    __tablename__ = "hubs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    ip = Column(String, nullable=False)
    last_seen = Column(DateTime, default=datetime.utcnow)

    nodes = relationship("Node", back_populates="hub", cascade="all, delete-orphan")

class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True)
    hub_id = Column(Integer, ForeignKey("hubs.id", ondelete="CASCADE"), nullable=False)
    ip = Column(String, nullable=True)
    location = Column(String, nullable=True)
    status = Column(String, nullable=True)
    sensor_count = Column(Integer, default=0)

    hub = relationship("Hub", back_populates="nodes")
    sensors = relationship("Sensor", back_populates="node", cascade="all, delete-orphan")

class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False)
    type = Column(String, nullable=False)
    pin = Column(String, nullable=False)
    status = Column(String, nullable=True)

    node = relationship("Node", back_populates="sensors")
