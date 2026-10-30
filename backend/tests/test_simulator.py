from app.models import SensorReading, SimState
from app.services.simulator import generate_reading, get_or_create_sim_state
from sqlalchemy import select


def test_generate_reading_normal(db_session):
    reading = generate_reading(db_session)
    assert reading is not None
    assert reading.flow_in > 50
    assert abs(reading.flow_in - reading.flow_out) < 5


def test_leak_injection_creates_imbalance(db_session):
    state = get_or_create_sim_state(db_session)
    state.leak_injected = True
    state.transport_running = True
    db_session.commit()

    reading = generate_reading(db_session)
    assert reading is not None
    assert reading.flow_in - reading.flow_out > 5


def test_transport_stop_near_zero_flow(db_session):
    state = get_or_create_sim_state(db_session)
    state.transport_running = False
    db_session.commit()

    reading = generate_reading(db_session)
    assert reading is not None
    assert reading.flow_in < 2
    assert reading.flow_out < 2


def test_sim_api_toggles(client, db_session):
    # Seed one reading via override session
    generate_reading(db_session)

    leak = client.post("/api/sim/leak", json={"enabled": True})
    assert leak.status_code == 200
    assert leak.json()["leak_injected"] is True

    transport = client.post("/api/sim/transport", json={"running": False})
    assert transport.status_code == 200
    assert transport.json()["transport_running"] is False

    status = client.get("/api/status")
    assert status.status_code == 200
    body = status.json()
    assert body["transport_status"] == "停輸"
    assert body["leak_injected"] is True

    latest = client.get("/api/readings/latest?limit=5")
    assert latest.status_code == 200
    assert len(latest.json()) >= 1
