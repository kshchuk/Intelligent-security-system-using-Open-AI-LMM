from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import crud, schemas
from database import SessionLocal

router = APIRouter(prefix="/hubs/{hub_id}/nodes", tags=["nodes"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[schemas.Node])
def read_nodes(hub_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_nodes(db, hub_id, skip, limit)

@router.post("/", response_model=schemas.Node, status_code=status.HTTP_201_CREATED)
def create_node(hub_id: int, node: schemas.NodeCreate, db: Session = Depends(get_db)):
    return crud.create_node(db, hub_id, node)

# For single node operations, mount under /nodes
single = APIRouter(prefix="/nodes", tags=["nodes"])

@single.get("/{node_id}", response_model=schemas.Node)
def read_node(node_id: int, db: Session = Depends(get_db)):
    db_node = crud.get_node(db, node_id)
    if not db_node:
        raise HTTPException(status_code=404, detail="Node not found")
    return db_node

@single.put("/{node_id}", response_model=schemas.Node)
def update_node(node_id: int, node: schemas.NodeCreate, db: Session = Depends(get_db)):
    db_node = crud.update_node(db, node_id, node)
    if not db_node:
        raise HTTPException(status_code=404, detail="Node not found")
    return db_node

@single.delete("/{node_id}", response_model=schemas.Node)
def delete_node(node_id: int, db: Session = Depends(get_db)):
    db_node = crud.delete_node(db, node_id)
    if not db_node:
        raise HTTPException(status_code=404, detail="Node not found")
    return db_node

# We’ll include both routers under the app
# router.include_router(single)
