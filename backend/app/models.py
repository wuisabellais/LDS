from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Pipeline(Base):
    __tablename__ = "pipeline"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    length_m: Mapped[float] = mapped_column(Float, nullable=False)
    diameter_m: Mapped[float] = mapped_column(Float, nullable=False)
    content_type: Mapped[str] = mapped_column(String(64), nullable=False)


class SensorReading(Base):
    __tablename__ = "sensor_reading"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ts: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    pressure_in: Mapped[float] = mapped_column(Float, nullable=False)
    pressure_out: Mapped[float] = mapped_column(Float, nullable=False)
    flow_in: Mapped[float] = mapped_column(Float, nullable=False)
    flow_out: Mapped[float] = mapped_column(Float, nullable=False)
    temperature: Mapped[float] = mapped_column(Float, nullable=False)


class DetectionResult(Base):
    __tablename__ = "detection_result"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ts: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    method: Mapped[str] = mapped_column(String(64), nullable=False)
    leak_suspected: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False, default="normal")
    metrics_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class SimState(Base):
    __tablename__ = "sim_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    leak_injected: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    transport_running: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
