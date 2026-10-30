from pathlib import Path

# Repo root: LDS/ (parent of backend/)
REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
DATABASE_PATH = DATA_DIR / "lds.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

SIM_INTERVAL_SECONDS = 2.0

# Nominal operating point for simulator
NOMINAL_PRESSURE_IN = 5.0  # MPa
NOMINAL_PRESSURE_OUT = 4.2  # MPa
NOMINAL_FLOW = 120.0  # m3/h
NOMINAL_TEMPERATURE = 35.0  # C

# Detection thresholds (simplified MVP)
FLOW_IMBALANCE_WATCH = 3.0  # m3/h
FLOW_IMBALANCE_ALARM = 8.0
GRADIENT_DEVIATION_WATCH = 0.15  # relative
GRADIENT_DEVIATION_ALARM = 0.35
PRESSURE_WAVE_WATCH = 0.08  # MPa step
PRESSURE_WAVE_ALARM = 0.2
