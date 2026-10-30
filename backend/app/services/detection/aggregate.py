from typing import Any, Dict, List, Optional

from app.models import Pipeline, SensorReading
from app.services.detection.flow_imbalance import evaluate_flow_imbalance
from app.services.detection.gradient import evaluate_pressure_gradient
from app.services.detection.pressure_wave import evaluate_pressure_wave


def run_all_methods(
    reading: SensorReading,
    pipeline: Pipeline,
    previous: Optional[SensorReading] = None,
) -> List[Dict[str, Any]]:
    return [
        evaluate_pressure_gradient(reading, pipeline),
        evaluate_flow_imbalance(reading, previous),
        evaluate_pressure_wave(reading, previous),
    ]


def aggregate_monitor_status(results: List[Dict[str, Any]]) -> str:
    """Map method severities to 正常|觀察|告警 labels used by the API/UI."""
    severities = {r.get("severity", "normal") for r in results}
    if "alarm" in severities:
        return "告警"
    if "watch" in severities:
        return "觀察"
    return "正常"
