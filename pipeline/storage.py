import hashlib
import json
import os
import sqlite3
from pathlib import Path

import joblib
import pandas as pd


ROOT = Path(os.getenv('SHARED_DIR', '/opt/project/shared'))
WINDOW_MONTHS = 3
HISTORY_MONTHS = 36
BATCH_SIZE = 3000


def connect():
    return sqlite3.connect(ROOT / 'data.db', timeout=30)


def month_after(month, count=1):
    return str(pd.Period(month, freq='M') + count)


def run_folder(kind, run_id):
    key = hashlib.sha256(run_id.encode()).hexdigest()[:20]
    path = ROOT / 'runs' / kind / key
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_json(path):
    return json.loads(Path(path).read_text())


def write_json(path, data):
    path = Path(path)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, indent=2))
    os.replace(temporary, path)


def save_model(path, model):
    temporary = Path(path).with_suffix('.tmp')
    joblib.dump(model, temporary)
    os.replace(temporary, path)


def current_model():
    return read_json(ROOT / 'models' / 'current.json')
