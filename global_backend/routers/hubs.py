from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import crud, schemas
from database import SessionLocal

router = APIRouter(prefix="/hubs", tags=["hubs"])

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[schemas.Hub])
def read_hubs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_hubs(db, skip=skip, limit=limit)

@router.post("/", response_model=schemas.Hub, status_code=status.HTTP_201_CREATED)
def create_hub(hub: schemas.HubCreate, db: Session = Depends(get_db)):
    return crud.create_hub(db, hub)

@router.get("/{hub_id}", response_model=schemas.Hub)
def read_hub(hub_id: int, db: Session = Depends(get_db)):
    db_hub = crud.get_hub(db, hub_id)
    if not db_hub:
        raise HTTPException(status_code=404, detail="Hub not found")
    return db_hub

@router.put("/{hub_id}", response_model=schemas.Hub)
def update_hub(hub_id: int, hub: schemas.HubCreate, db: Session = Depends(get_db)):
    db_hub = crud.update_hub(db, hub_id, hub)
    if not db_hub:
        raise HTTPException(status_code=404, detail="Hub not found")
    return db_hub

@router.delete("/{hub_id}", response_model=schemas.Hub)
def delete_hub(hub_id: int, db: Session = Depends(get_db)):
    db_hub = crud.delete_hub(db, hub_id)
    if not db_hub:
        raise HTTPException(status_code=404, detail="Hub not found")
    return db_hub
