import json
import os
import sqlite3
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from kafka import KafkaProducer


def main():
    path = Path(os.getenv('SHARED_DIR', '/opt/project/shared')) / 'data.db'
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    rows = [dict(row) for row in connection.execute('SELECT * FROM labeled_transactions LIMIT 3000')]
    connection.close()
    for row in rows:
        row.pop('target')
    producer = KafkaProducer(
        bootstrap_servers=os.getenv('KAFKA_BROKERS', 'kafka:9092'), acks='all',
        value_serializer=lambda value: json.dumps(value).encode(),
    )
    index = 0
    while True:
        data = dict(rows[index % len(rows)])
        data['transaction_time'] = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        transaction_id = str(uuid.uuid4())
        producer.send('transactions', key=transaction_id.encode(), value={
            'transaction_id': transaction_id, 'data': data,
        }).get(timeout=30)
        index += 1
        time.sleep(1)


if __name__ == '__main__':
    main()
