from database import SessionLocal, Base, engine
from models import Hub, Node, Sensor
from datetime import datetime

# Ensure tables exist
Base.metadata.create_all(bind=engine)

def populate():
    session = SessionLocal()
    try:
        # Clear existing data (optional)
        session.query(Sensor).delete()
        session.query(Node).delete()
        session.query(Hub).delete()
        session.commit()

        # Create 3 hubs
        for i in range(1, 4):
            hub = Hub(
                name=f"MockHub{i}",
                ip=f"192.168.10.{i}",
                last_seen=datetime.utcnow()
            )
            session.add(hub)
            session.flush()  # assign hub.id

            # For each hub, create 2 nodes
            for j in range(1, 3):
                node = Node(
                    hub_id=hub.id,
                    ip=f"10.0.{i}.{j}",
                    location=f"Location_{i}_{j}",
                    status="online",
                    sensor_count=0
                )
                session.add(node)
                session.flush()  # assign node.id

                # For each node, create 3 sensors
                types = ["PIR", "Camera", "Temperature"]
                for pin_idx, sensor_type in enumerate(types, start=1):
                    sensor = Sensor(
                        node_id=node.id,
                        type=sensor_type,
                        pin=str(pin_idx),
                        status="active"
                    )
                    session.add(sensor)
                    # increment sensor_count on the node
                    node.sensor_count = (node.sensor_count or 0) + 1

        # Commit all at once
        session.commit()
        print("✅ Database populated with mock data!")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    populate()
