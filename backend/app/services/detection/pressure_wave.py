from typing import Any, Dict, Optional

from app.config import PRESSURE_WAVE_ALARM, PRESSURE_WAVE_WATCH
from app.models import SensorReading


def evaluate_pressure_wave(
    reading: SensorReading,
    previous: Optional[SensorReading] = None,
) -> Dict[str, Any]:
    """Detect abrupt pressure steps as a simplified pressure-wave signature."""
    step_in = 0.0
    step_out = 0.0
    if previous is not None:
        step_in = abs(reading.pressure_in - previous.pressure_in)
        step_out = abs(reading.pressure_out - previous.pressure_out)

    max_step = max(step_in, step_out)

    if max_step >= PRESSURE_WAVE_ALARM:
        severity = "alarm"
        leak_suspected = True
    elif max_step >= PRESSURE_WAVE_WATCH:
        severity = "watch"
        leak_suspected = True
    else:
        severity = "normal"
        leak_suspected = False

    return {
        "method": "pressure_wave",
        "leak_suspected": leak_suspected,
        "severity": severity,
        "metrics": {
            "pressure_step_in_mpa": round(step_in, 6),
            "pressure_step_out_mpa": round(step_out, 6),
            "max_step_mpa": round(max_step, 6),
        },
    }
