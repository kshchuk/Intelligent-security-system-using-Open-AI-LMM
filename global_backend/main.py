from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import hubs, nodes, sensors
from routers.hub_sync import router as hub_sync_router
from routers.auth import router as auth_router, get_current_active_user

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Test IoT Security Management API",
    description="CRUD for Hubs, Nodes, and Sensors. Requires authentication via OAuth2 JWT.",
    version="0.0.1"
)

# Allow all origins for now (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(auth_router)
app.include_router(hubs.router, dependencies=[Depends(get_current_active_user)])
app.include_router(nodes.router, dependencies=[Depends(get_current_active_user)])
app.include_router(nodes.single, dependencies=[Depends(get_current_active_user)])
app.include_router(sensors.router, dependencies=[Depends(get_current_active_user)])
app.include_router(sensors.single, dependencies=[Depends(get_current_active_user)])
app.include_router(hub_sync_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

