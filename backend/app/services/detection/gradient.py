from typing import Any, Dict, Optional

from app.config import GRADIENT_DEVIATION_ALARM, GRADIENT_DEVIATION_WATCH
from app.models import Pipeline, SensorReading


def evaluate_pressure_gradient(
    reading: SensorReading,
    pipeline: Pipeline,
) -> Dict[str, Any]:
    """Compare measured pressure drop per km to a simple theoretical gradient."""
    length_km = max(pipeline.length_m / 1000.0, 0.001)
    measured_dp = reading.pressure_in - reading.pressure_out
    measured_grad = measured_dp / length_km

    # Simplified Darcy-ish proxy: theoretical gradient scales with flow^2
    flow_avg = (reading.flow_in + reading.flow_out) / 2.0
    theoretical_grad = 0.02 + 1.5e-5 * (flow_avg**2)

    if theoretical_grad <= 1e-9:
        deviation = 0.0
    else:
        deviation = abs(measured_grad - theoretical_grad) / theoretical_grad

    if deviation >= GRADIENT_DEVIATION_ALARM:
        severity = "alarm"
        leak_suspected = True
    elif deviation >= GRADIENT_DEVIATION_WATCH:
        severity = "watch"
        leak_suspected = True
    else:
        severity = "normal"
        leak_suspected = False

    return {
        "method": "pressure_gradient",
        "leak_suspected": leak_suspected,
        "severity": severity,
        "metrics": {
            "measured_gradient_mpa_per_km": round(measured_grad, 6),
            "theoretical_gradient_mpa_per_km": round(theoretical_grad, 6),
            "relative_deviation": round(deviation, 6),
        },
    }
