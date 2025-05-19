# routers/sensors.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import crud, schemas
from database import SessionLocal

router = APIRouter(prefix="/nodes/{node_id}/sensors", tags=["sensors"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[schemas.Sensor])
def read_sensors(node_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_sensors(db, node_id, skip, limit)

@router.post("/", response_model=schemas.Sensor, status_code=status.HTTP_201_CREATED)
def create_sensor(node_id: int, sensor: schemas.SensorCreate, db: Session = Depends(get_db)):
    return crud.create_sensor(db, node_id, sensor)

single = APIRouter(prefix="/sensors", tags=["sensors"])

@single.get("/{sensor_id}", response_model=schemas.Sensor)
def read_sensor(sensor_id: int, db: Session = Depends(get_db)):
    db_sensor = crud.get_sensor(db, sensor_id)
    if not db_sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return db_sensor

@single.put("/{sensor_id}", response_model=schemas.Sensor)
def update_sensor(sensor_id: int, sensor: schemas.SensorCreate, db: Session = Depends(get_db)):
    db_sensor = crud.update_sensor(db, sensor_id, sensor)
    if not db_sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return db_sensor

@single.delete("/{sensor_id}", response_model=schemas.Sensor)
def delete_sensor(sensor_id: int, db: Session = Depends(get_db)):
    db_sensor = crud.delete_sensor(db, sensor_id)
    if not db_sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return db_sensor

router.include_router(single)
