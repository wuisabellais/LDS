from datetime import datetime, timedelta

from app.models import Pipeline, SensorReading
from app.services.detection import (
    aggregate_monitor_status,
    evaluate_flow_imbalance,
    evaluate_pressure_gradient,
    evaluate_pressure_wave,
)


def _pipeline() -> Pipeline:
    return Pipeline(
        id=1,
        name="t",
        length_m=25000.0,
        diameter_m=0.6,
        content_type="原油",
    )


def test_flow_imbalance_normal_vs_leak():
    normal = SensorReading(
        id=1,
        ts=datetime.utcnow(),
        pressure_in=5.0,
        pressure_out=4.2,
        flow_in=120.0,
        flow_out=119.5,
        temperature=35.0,
    )
    leak = SensorReading(
        id=2,
        ts=datetime.utcnow(),
        pressure_in=5.0,
        pressure_out=3.7,
        flow_in=120.0,
        flow_out=105.0,
        temperature=35.0,
    )
    assert evaluate_flow_imbalance(normal)["severity"] == "normal"
    assert evaluate_flow_imbalance(leak)["leak_suspected"] is True


def test_pressure_gradient_flags_large_deviation():
    pipeline = _pipeline()
    # Large measured drop vs low flow → high relative deviation
    reading = SensorReading(
        id=1,
        ts=datetime.utcnow(),
        pressure_in=5.0,
        pressure_out=2.0,
        flow_in=10.0,
        flow_out=10.0,
        temperature=35.0,
    )
    result = evaluate_pressure_gradient(reading, pipeline)
    assert result["method"] == "pressure_gradient"
    assert result["leak_suspected"] is True


def test_pressure_wave_detects_step():
    prev = SensorReading(
        id=1,
        ts=datetime.utcnow(),
        pressure_in=5.0,
        pressure_out=4.2,
        flow_in=120.0,
        flow_out=120.0,
        temperature=35.0,
    )
    now = SensorReading(
        id=2,
        ts=prev.ts + timedelta(seconds=2),
        pressure_in=5.0,
        pressure_out=3.9,
        flow_in=120.0,
        flow_out=120.0,
        temperature=35.0,
    )
    result = evaluate_pressure_wave(now, prev)
    assert result["leak_suspected"] is True
    assert result["severity"] in {"watch", "alarm"}


def test_aggregate_monitor_status():
    assert aggregate_monitor_status([{"severity": "normal"}]) == "正常"
    assert aggregate_monitor_status([{"severity": "watch"}]) == "觀察"
    assert (
        aggregate_monitor_status([{"severity": "watch"}, {"severity": "alarm"}])
        == "告警"
    )
