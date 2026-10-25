import json
import logging
import os

import pandas as pd
from kafka import KafkaConsumer, KafkaProducer

from fraud_detector.src.scorer import make_pred


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
BROKERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
INPUT_TOPIC = 'transactions'
OUTPUT_TOPIC = 'scores'


def main():
    consumer = KafkaConsumer(
        INPUT_TOPIC, bootstrap_servers=BROKERS, group_id='fraud-scorer',
        auto_offset_reset='earliest', enable_auto_commit=False,
        max_poll_records=1, value_deserializer=lambda value: json.loads(value),
    )
    producer = KafkaProducer(
        bootstrap_servers=BROKERS, acks='all',
        value_serializer=lambda value: json.dumps(value).encode('utf-8'),
    )
    logging.info('Waiting for transactions')
    try:
        for message in consumer:
            transaction = message.value
            result = make_pred(pd.DataFrame([transaction['data']]))
            result['transaction_id'] = transaction['transaction_id']
            producer.send(OUTPUT_TOPIC, key=result['transaction_id'].encode(),
                          value=result).get(timeout=30)
            consumer.commit()
            logging.info('Scored transaction: score=%.6f, fraud_flag=%s, model_version=%s',
                         result['score'], result['fraud_flag'], result['model_version'])
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()
        producer.close()


if __name__ == '__main__':
    main()
