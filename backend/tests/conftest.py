import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Use in-memory DB for tests before app imports bind to disk.
os.environ.setdefault("LDS_TEST_MODE", "1")

from app.db import get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Base, Pipeline, SimState  # noqa: E402


@pytest.fixture()
def db_session(tmp_path: Path):
    db_path = tmp_path / "test.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    session.add(
        Pipeline(
            name="測試管線",
            length_m=25000.0,
            diameter_m=0.6,
            content_type="原油",
        )
    )
    session.add(SimState(leak_injected=False, transport_running=True))
    session.commit()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def client(db_session):
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    # Avoid starting background simulator during request tests
    with TestClient(app, raise_server_exceptions=True) as test_client:
        yield test_client
    app.dependency_overrides.clear()
