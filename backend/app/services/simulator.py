import asyncio
import json
import logging
import random
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import (
    NOMINAL_FLOW,
    NOMINAL_PRESSURE_IN,
    NOMINAL_PRESSURE_OUT,
    NOMINAL_TEMPERATURE,
    SIM_INTERVAL_SECONDS,
)
from app.db import SessionLocal
from app.models import DetectionResult, Pipeline, SensorReading, SimState
from app.services.detection import run_all_methods

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def get_or_create_sim_state(session: Session) -> SimState:
    state = session.scalar(select(SimState).limit(1))
    if state is None:
        state = SimState(leak_injected=False, transport_running=True)
        session.add(state)
        session.commit()
        session.refresh(state)
    return state


def generate_reading(session: Session) -> Optional[SensorReading]:
    pipeline = session.scalar(select(Pipeline).limit(1))
    state = get_or_create_sim_state(session)
    if pipeline is None:
        return None

    previous = session.scalar(
        select(SensorReading).order_by(SensorReading.ts.desc()).limit(1)
    )

    noise = lambda scale: random.uniform(-scale, scale)  # noqa: E731

    if state.transport_running:
        flow_in = NOMINAL_FLOW + noise(1.5)
        flow_out = NOMINAL_FLOW + noise(1.5)
        pressure_in = NOMINAL_PRESSURE_IN + noise(0.02)
        pressure_out = NOMINAL_PRESSURE_OUT + noise(0.02)
    else:
        flow_in = abs(noise(0.2))
        flow_out = abs(noise(0.2))
        pressure_in = 1.0 + noise(0.02)
        pressure_out = 0.95 + noise(0.02)

    if state.leak_injected and state.transport_running:
        # Leak: outlet flow drops, outlet pressure drops sharply relative to inlet
        flow_out = max(0.0, flow_out - 12.0 + noise(1.0))
        pressure_out = max(0.1, pressure_out - 0.45 + noise(0.03))
        pressure_in = pressure_in - 0.05 + noise(0.02)

    temperature = NOMINAL_TEMPERATURE + noise(0.5)

    reading = SensorReading(
        ts=_utcnow(),
        pressure_in=round(pressure_in, 4),
        pressure_out=round(pressure_out, 4),
        flow_in=round(flow_in, 4),
        flow_out=round(flow_out, 4),
        temperature=round(temperature, 4),
    )
    session.add(reading)
    session.flush()

    results = run_all_methods(reading, pipeline, previous)
    for result in results:
        session.add(
            DetectionResult(
                ts=reading.ts,
                method=result["method"],
                leak_suspected=bool(result["leak_suspected"]),
                severity=str(result["severity"]),
                metrics_json=json.dumps(result["metrics"], ensure_ascii=False),
            )
        )

    session.commit()
    session.refresh(reading)
    return reading


async def simulation_loop(stop_event: asyncio.Event) -> None:
    logger.info("Simulation loop started (interval=%.1fs)", SIM_INTERVAL_SECONDS)
    while not stop_event.is_set():
        try:
            with SessionLocal() as session:
                generate_reading(session)
        except Exception:
            logger.exception("Simulator tick failed")
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=SIM_INTERVAL_SECONDS)
        except asyncio.TimeoutError:
            continue
    logger.info("Simulation loop stopped")
