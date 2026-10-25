from pathlib import Path

import pandas as pd

from pipeline.storage import (
    BATCH_SIZE, HISTORY_MONTHS, connect, current_model, month_after,
    read_json, run_folder, write_json,
)


def sample_month(run_id):
    folder = run_folder('supply', run_id)
    if (folder / 'batch.json').exists():
        return str(folder)
    with connect() as connection:
        frame = pd.read_sql_query('SELECT * FROM labeled_transactions', connection)
    month = month_after(frame.transaction_time.str[:7].max())
    if month > month_after(current_model()['month']):
        return None
    batch = frame.sample(BATCH_SIZE, replace=True, random_state=int(month.replace('-', ''))).copy()
    start = pd.Timestamp(month)
    old_time = pd.to_datetime(batch.transaction_time)
    day = old_time.dt.day.clip(upper=start.days_in_month) - 1
    batch['transaction_time'] = (
        start + pd.to_timedelta(day, unit='D') + (old_time - old_time.dt.normalize())
    ).dt.strftime('%Y-%m-%d %H:%M:%S')
    batch.to_csv(folder / 'batch.csv', index=False)
    write_json(folder / 'batch.json', {'month': month, 'run_id': run_id})
    return str(folder)


def append_month(folder):
    folder = Path(folder)
    info = read_json(folder / 'batch.json')
    frame = pd.read_csv(folder / 'batch.csv')
    with connect() as connection:
        connection.execute('BEGIN IMMEDIATE')
        if connection.execute('SELECT 1 FROM supply_runs WHERE run_id = ?', (info['run_id'],)).fetchone():
            return info['month']
        latest = connection.execute('SELECT MAX(transaction_time) FROM labeled_transactions').fetchone()[0][:7]
        if info['month'] != month_after(latest):
            return None
        columns = ', '.join(frame.columns)
        placeholders = ', '.join('?' for _ in frame.columns)
        connection.executemany(
            f'INSERT INTO labeled_transactions ({columns}) VALUES ({placeholders})',
            frame.itertuples(index=False, name=None),
        )
        cutoff = month_after(info['month'], 1 - HISTORY_MONTHS) + '-01'
        connection.execute('DELETE FROM labeled_transactions WHERE transaction_time < ?', (cutoff,))
        connection.execute('INSERT INTO supply_runs VALUES (?, ?)', (info['run_id'], info['month']))
    return info['month']
