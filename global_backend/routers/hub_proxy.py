from fastapi import APIRouter, Depends, HTTPException, Response, status, WebSocket
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

import requests
import websockets

from database import SessionLocal
import crud
from routers.auth import get_current_active_user


router = APIRouter(
    prefix="/hubs/{hub_id}",
    tags=["hub_proxy"],
    dependencies=[Depends(get_current_active_user)],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/alerts", response_class=Response)
def proxy_alerts(hub_id: int, db: Session = Depends(get_db)):
    """
    Proxy REST call from backend to the hub's /alerts endpoint.
    """
    hub = crud.get_hub(db, hub_id)
    if not hub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hub not found")
    upstream = f"http://{hub.ip}:8000/alerts"
    resp = requests.get(upstream)
    return Response(
        content=resp.content,
        status_code=resp.status_code,
        media_type=resp.headers.get("content-type", "application/json"),
    )


@router.websocket("/ws/alerts")
async def proxy_ws_alerts(websocket: WebSocket, hub_id: int, db: Session = Depends(get_db)):
    """
    Proxy WebSocket from backend to the hub's /ws/alerts endpoint.
    """
    await websocket.accept()
    hub = crud.get_hub(db, hub_id)
    if not hub:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    uri = f"ws://{hub.ip}:8000/ws/alerts"
    try:
        async with websockets.connect(uri) as upstream_ws:
            async for msg in upstream_ws:
                await websocket.send_text(msg)
    except Exception:
        pass
    finally:
        await websocket.close()