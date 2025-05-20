from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from database import SessionLocal
import crud
import schemas

router = APIRouter(prefix="/hub", tags=["hub_sync"])

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.put("/register", status_code=status.HTTP_200_OK)
def register_hub(hub: schemas.HubCreate, db: Session = Depends(get_db)):
    """
    Called by a hub on boot.
    """

    # Check if the hub already exists
    db_hub = crud.get_hub_by_name(db, hub.name)
    if db_hub:
        # Update the existing hub
        db_hub.ip = hub.ip
        db_hub.last_seen = datetime.utcnow()
        crud.update_hub(db, db_hub.id, db_hub)
        db.commit()
        return {"status": "updated", "hub_id": db_hub.id}
    else:
        # Create a new hub
        db_hub = crud.create_hub(db, hub)
        hub_id = db_hub.id

    db.commit()
    return {"status": "registered", "hub_id": hub_id}

@router.get("/{hub_id}/config", response_model=schemas.Hub)
def get_hub_config(hub_id: int, db: Session = Depends(get_db)):
    """
    Returns the Hub with nested nodes and sensors (including each sensor.status).
    HubApp can call this for full config.
    """
    db_hub = crud.get_hub(db, hub_id)
    if not db_hub:
        raise HTTPException(status_code=404, detail="Hub not found")

    db_hub.last_seen = datetime.utcnow()
    crud.update_hub(db, hub_id, db_hub)
    db.commit()
    return db_hub