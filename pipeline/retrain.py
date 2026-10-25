from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

from fraud_detector.src.preprocessing import new_model
from pipeline.storage import (
    ROOT, WINDOW_MONTHS, connect, current_model, month_after,
    read_json, run_folder, save_model, write_json,
)


def prepare_data(run_id):
    folder = run_folder('retrain', run_id)
    if (folder / 'plan.json').exists():
        return str(folder)
    current = current_model()
    month = month_after(current['month'])
    first = month_after(month, 1 - WINDOW_MONTHS)
    with connect() as connection:
        frame = pd.read_sql_query(
            'SELECT * FROM labeled_transactions WHERE transaction_time >= ? AND transaction_time < ?',
            connection, params=(first + '-01', month_after(month) + '-01'),
        )
    expected = {month_after(first, offset) for offset in range(WINDOW_MONTHS)}
    if set(frame.transaction_time.str[:7]) != expected:
        return None
    train = frame[frame.transaction_time < month + '-01']
    test = frame[frame.transaction_time >= month + '-01']
    train.to_csv(folder / 'train.csv', index=False)
    test.to_csv(folder / 'test.csv', index=False)
    write_json(folder / 'plan.json', {
        'month': month, 'train_months': sorted(expected - {month}),
        'test_month': month, 'baseline': current,
        'version': 'model_' + month.replace('-', '') + '_' + folder.name,
    })
    return str(folder)


def train_model(folder):
    folder = Path(folder)
    train = pd.read_csv(folder / 'train.csv')
    model = new_model().fit(train, train.target)
    save_model(folder / 'new_model.joblib', model)
    return str(folder)


def metrics(model, test):
    scores = model.predict_proba(test)[:, 1]
    return {
        'average_precision': float(average_precision_score(test.target, scores)),
        'roc_auc': float(roc_auc_score(test.target, scores)),
    }


def compare_models(folder):
    folder = Path(folder)
    plan = read_json(folder / 'plan.json')
    test = pd.read_csv(folder / 'test.csv')
    new_metrics = metrics(joblib.load(folder / 'new_model.joblib'), test)
    baseline = metrics(joblib.load(ROOT / 'models' / plan['baseline']['file']), test)
    report = {
        'new_model': new_metrics, 'baseline': baseline,
        'accepted': all(new_metrics[name] >= baseline[name] for name in new_metrics),
        'test_month': plan['month'], 'test_rows': len(test),
    }
    write_json(folder / 'metrics.json', report)
    print(report)
    if not report['accepted']:
        return None
    return str(folder)


def publish_model(folder):
    folder = Path(folder)
    plan = read_json(folder / 'plan.json')
    report = read_json(folder / 'metrics.json')
    current = current_model()
    if current['month'] >= plan['month']:
        return current
    if not report['accepted']:
        return None
    filename = plan['version'] + '.joblib'
    save_model(ROOT / 'models' / filename, joblib.load(folder / 'new_model.joblib'))
    manifest = {
        'version': plan['version'], 'file': filename, 'month': plan['month'],
        'metrics': report,
    }
    write_json(ROOT / 'models' / 'current.json', manifest)
    return manifest
