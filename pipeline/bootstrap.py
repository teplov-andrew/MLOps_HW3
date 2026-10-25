import pandas as pd

from fraud_detector.src.preprocessing import new_model
from pipeline.storage import ROOT, WINDOW_MONTHS, connect, month_after, save_model, write_json


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    (ROOT / 'models').mkdir(exist_ok=True)
    with connect() as connection:
        exists = connection.execute(
            "SELECT name FROM sqlite_master WHERE name = 'labeled_transactions'"
        ).fetchone()
        if not exists:
            data = pd.read_csv('/data/train.csv', usecols=[
                'transaction_time', 'amount', 'population_city', 'lat', 'lon',
                'merchant_lat', 'merchant_lon', 'target',
            ])
            data['transaction_time'] = pd.to_datetime(data.transaction_time).dt.strftime('%Y-%m-%d %H:%M:%S')
            data.to_sql('labeled_transactions', connection, index=False)
        connection.execute('CREATE TABLE IF NOT EXISTS supply_runs (run_id TEXT PRIMARY KEY, month TEXT)')
        data = pd.read_sql_query('SELECT * FROM labeled_transactions', connection)

    if not (ROOT / 'models' / 'current.json').exists():
        month = data.transaction_time.str[:7].max()
        first = month_after(month, 1 - WINDOW_MONTHS)
        train = data[(data.transaction_time >= first + '-01') & (data.transaction_time < month + '-01')]
        model = new_model().fit(train, train.target)
        save_model(ROOT / 'models' / 'model_initial.joblib', model)
        write_json(ROOT / 'models' / 'current.json', {
            'version': 'initial', 'file': 'model_initial.joblib', 'month': month,
        })


if __name__ == '__main__':
    main()
