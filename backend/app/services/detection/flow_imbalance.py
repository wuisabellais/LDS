from typing import Any, Dict, Optional

from app.config import FLOW_IMBALANCE_ALARM, FLOW_IMBALANCE_WATCH
from app.models import SensorReading


def evaluate_flow_imbalance(
    reading: SensorReading,
    previous: Optional[SensorReading] = None,
) -> Dict[str, Any]:
    """Flag inlet/outlet flow imbalance and rapid flow change."""
    imbalance = abs(reading.flow_in - reading.flow_out)
    change_rate = 0.0
    if previous is not None:
        dt = (reading.ts - previous.ts).total_seconds()
        if dt > 0:
            avg_now = (reading.flow_in + reading.flow_out) / 2.0
            avg_prev = (previous.flow_in + previous.flow_out) / 2.0
            change_rate = abs(avg_now - avg_prev) / dt

    score = imbalance + 0.5 * change_rate

    if score >= FLOW_IMBALANCE_ALARM or imbalance >= FLOW_IMBALANCE_ALARM:
        severity = "alarm"
        leak_suspected = True
    elif score >= FLOW_IMBALANCE_WATCH or imbalance >= FLOW_IMBALANCE_WATCH:
        severity = "watch"
        leak_suspected = True
    else:
        severity = "normal"
        leak_suspected = False

    return {
        "method": "flow_imbalance",
        "leak_suspected": leak_suspected,
        "severity": severity,
        "metrics": {
            "imbalance_m3h": round(imbalance, 4),
            "flow_change_rate_m3h_s": round(change_rate, 4),
        },
    }
