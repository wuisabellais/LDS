import json
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import DetectionResult, Pipeline, SensorReading, SimState
from app.schemas import (
    DetectionOut,
    HealthResponse,
    MethodStatus,
    PipelineOut,
    SensorReadingOut,
    SimStateOut,
    SimToggleRequest,
    StatusResponse,
    TransportToggleRequest,
)
from app.services.detection import aggregate_monitor_status
from app.services.simulator import get_or_create_sim_state

router = APIRouter(prefix="/api")


def _parse_metrics(raw: str) -> dict:
    try:
        data = json.loads(raw or "{}")
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/pipeline", response_model=PipelineOut)
def get_pipeline(db: Session = Depends(get_db)) -> Pipeline:
    pipeline = db.scalar(select(Pipeline).limit(1))
    if pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not configured")
    return pipeline


@router.get("/readings/latest", response_model=List[SensorReadingOut])
def latest_readings(
    limit: int = Query(default=60, ge=1, le=500),
    db: Session = Depends(get_db),
) -> List[SensorReading]:
    rows = db.scalars(
        select(SensorReading).order_by(SensorReading.ts.desc()).limit(limit)
    ).all()
    return list(reversed(rows))


@router.get("/readings", response_model=List[SensorReadingOut])
def readings_range(
    from_ts: datetime = Query(alias="from"),
    to_ts: datetime = Query(alias="to"),
    db: Session = Depends(get_db),
) -> List[SensorReading]:
    rows = db.scalars(
        select(SensorReading)
        .where(SensorReading.ts >= from_ts, SensorReading.ts <= to_ts)
        .order_by(SensorReading.ts.asc())
    ).all()
    return list(rows)


@router.get("/detections", response_model=List[DetectionOut])
def detections_range(
    from_ts: datetime = Query(alias="from"),
    to_ts: datetime = Query(alias="to"),
    db: Session = Depends(get_db),
) -> List[DetectionOut]:
    rows = db.scalars(
        select(DetectionResult)
        .where(DetectionResult.ts >= from_ts, DetectionResult.ts <= to_ts)
        .order_by(DetectionResult.ts.asc())
    ).all()
    return [
        DetectionOut(
            id=row.id,
            ts=row.ts,
            method=row.method,
            leak_suspected=row.leak_suspected,
            severity=row.severity,
            metrics=_parse_metrics(row.metrics_json),
        )
        for row in rows
    ]


@router.get("/status", response_model=StatusResponse)
def get_status(db: Session = Depends(get_db)) -> StatusResponse:
    pipeline = db.scalar(select(Pipeline).limit(1))
    state = get_or_create_sim_state(db)
    latest_rows = db.scalars(
        select(SensorReading).order_by(SensorReading.ts.desc()).limit(2)
    ).all()
    latest = latest_rows[0] if latest_rows else None
    previous = latest_rows[1] if len(latest_rows) > 1 else None

    flow_change_rate: Optional[float] = None
    pressure_change_rate: Optional[float] = None
    if latest and previous:
        dt = (latest.ts - previous.ts).total_seconds()
        if dt > 0:
            flow_now = (latest.flow_in + latest.flow_out) / 2.0
            flow_prev = (previous.flow_in + previous.flow_out) / 2.0
            pressure_now = (latest.pressure_in + latest.pressure_out) / 2.0
            pressure_prev = (previous.pressure_in + previous.pressure_out) / 2.0
            flow_change_rate = round((flow_now - flow_prev) / dt, 4)
            pressure_change_rate = round((pressure_now - pressure_prev) / dt, 6)

    methods: List[MethodStatus] = []
    if latest:
        method_rows = db.scalars(
            select(DetectionResult)
            .where(DetectionResult.ts == latest.ts)
            .order_by(DetectionResult.method.asc())
        ).all()
        methods = [
            MethodStatus(
                method=row.method,
                leak_suspected=row.leak_suspected,
                severity=row.severity,
                metrics=_parse_metrics(row.metrics_json),
            )
            for row in method_rows
        ]

    monitor_status = aggregate_monitor_status(
        [
            {
                "severity": m.severity,
            }
            for m in methods
        ]
    )
    transport_status = "輸送中" if state.transport_running else "停輸"

    return StatusResponse(
        transport_status=transport_status,
        monitor_status=monitor_status,
        content_type=pipeline.content_type if pipeline else "未知",
        latest=SensorReadingOut.model_validate(latest) if latest else None,
        flow_change_rate=flow_change_rate,
        pressure_change_rate=pressure_change_rate,
        methods=methods,
        leak_injected=state.leak_injected,
        transport_running=state.transport_running,
    )


@router.post("/sim/leak", response_model=SimStateOut)
def set_leak(body: SimToggleRequest, db: Session = Depends(get_db)) -> SimStateOut:
    state = get_or_create_sim_state(db)
    state.leak_injected = body.enabled
    db.commit()
    db.refresh(state)
    return SimStateOut(
        leak_injected=state.leak_injected,
        transport_running=state.transport_running,
    )


@router.post("/sim/transport", response_model=SimStateOut)
def set_transport(
    body: TransportToggleRequest, db: Session = Depends(get_db)
) -> SimStateOut:
    state = get_or_create_sim_state(db)
    state.transport_running = body.running
    db.commit()
    db.refresh(state)
    return SimStateOut(
        leak_injected=state.leak_injected,
        transport_running=state.transport_running,
    )
