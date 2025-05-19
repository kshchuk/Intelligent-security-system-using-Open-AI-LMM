# crud.py
from sqlalchemy.orm import Session
import models, schemas
from datetime import datetime

# --- Hubs ---
def get_hubs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Hub).offset(skip).limit(limit).all()

def get_hub(db: Session, hub_id: int):
    return db.query(models.Hub).filter(models.Hub.id == hub_id).first()

def create_hub(db: Session, hub: schemas.HubCreate):
    db_hub = models.Hub(
        name=hub.name,
        ip=hub.ip,
        last_seen=hub.last_seen or datetime.utcnow()
    )
    db.add(db_hub)
    db.commit()
    db.refresh(db_hub)
    return db_hub

def update_hub(db: Session, hub_id: int, hub: schemas.HubCreate):
    db_hub = get_hub(db, hub_id)
    if not db_hub:
        return None
    db_hub.name = hub.name
    db_hub.ip = hub.ip
    db_hub.last_seen = hub.last_seen or db_hub.last_seen
    db.commit()
    db.refresh(db_hub)
    return db_hub

def delete_hub(db: Session, hub_id: int):
    db_hub = get_hub(db, hub_id)
    if db_hub:
        db.delete(db_hub)
        db.commit()
    return db_hub

# --- Nodes ---
def get_nodes(db: Session, hub_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Node)
        .filter(models.Node.hub_id == hub_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_node(db: Session, node_id: int):
    return db.query(models.Node).filter(models.Node.id == node_id).first()

def create_node(db: Session, hub_id: int, node: schemas.NodeCreate):
    db_node = models.Node(
        hub_id=hub_id,
        ip=node.ip,
        location=node.location,
        status=node.status,
        sensor_count=node.sensor_count or 0
    )
    db.add(db_node)
    db.commit()
    db.refresh(db_node)
    return db_node

def update_node(db: Session, node_id: int, node: schemas.NodeCreate):
    db_node = get_node(db, node_id)
    if not db_node:
        return None
    db_node.ip = node.ip
    db_node.location = node.location
    db_node.status = node.status
    db_node.sensor_count = node.sensor_count
    db.commit()
    db.refresh(db_node)
    return db_node

def delete_node(db: Session, node_id: int):
    db_node = get_node(db, node_id)
    if db_node:
        db.delete(db_node)
        db.commit()
    return db_node

# --- Sensors ---
def get_sensors(db: Session, node_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Sensor)
        .filter(models.Sensor.node_id == node_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_sensor(db: Session, sensor_id: int):
    return db.query(models.Sensor).filter(models.Sensor.id == sensor_id).first()

def create_sensor(db: Session, node_id: int, sensor: schemas.SensorCreate):
    db_sensor = models.Sensor(
        node_id=node_id,
        type=sensor.type,
        pin=sensor.pin,
        status=sensor.status
    )
    db.add(db_sensor)
    # update parent node's sensor_count
    parent = db.query(models.Node).get(node_id)
    if parent:
        parent.sensor_count = (parent.sensor_count or 0) + 1
    db.commit()
    db.refresh(db_sensor)
    return db_sensor

def update_sensor(db: Session, sensor_id: int, sensor: schemas.SensorCreate):
    db_sensor = get_sensor(db, sensor_id)
    if not db_sensor:
        return None
    db_sensor.type = sensor.type
    db_sensor.pin = sensor.pin
    db_sensor.status = sensor.status
    db.commit()
    db.refresh(db_sensor)
    return db_sensor

def delete_sensor(db: Session, sensor_id: int):
    db_sensor = get_sensor(db, sensor_id)
    if db_sensor:
        # update parent node's sensor_count
        parent = db_sensor.node
        if parent and parent.sensor_count:
            parent.sensor_count = parent.sensor_count - 1
        db.delete(db_sensor)
        db.commit()
    return db_sensor
