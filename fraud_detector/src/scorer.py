import logging
import os

import joblib

from pipeline.storage import ROOT, current_model


model = None
model_version = None
threshold = float(os.getenv('FRAUD_THRESHOLD', '0.5'))


def make_pred(df):
    global model, model_version
    current = current_model()
    if current['version'] != model_version:
        model = joblib.load(ROOT / 'models' / current['file'])
        model_version = current['version']
        logging.info('Loaded model %s', model_version)
    score = float(model.predict_proba(df)[0, 1])
    res = {'score': score, 'fraud_flag': int(score >= threshold), 'model_version': model_version}
    return res