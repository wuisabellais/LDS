from collections.abc import Generator

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.config import DATA_DIR, DATABASE_URL
from app.models import Base, Pipeline, SimState

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        if session.scalar(select(Pipeline).limit(1)) is None:
            session.add(
                Pipeline(
                    name="示範管線 A",
                    length_m=25000.0,
                    diameter_m=0.6,
                    content_type="原油",
                )
            )
        if session.scalar(select(SimState).limit(1)) is None:
            session.add(SimState(leak_injected=False, transport_running=True))
        session.commit()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
