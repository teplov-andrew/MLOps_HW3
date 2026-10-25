import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler


def run_preproc(df):
    time = pd.to_datetime(df['transaction_time'])
    amount = pd.to_numeric(df['amount'], errors='coerce').clip(lower=0)
    population = pd.to_numeric(df['population_city'], errors='coerce').clip(lower=0)
    hour = time.dt.hour + time.dt.minute / 60
    night = ((hour < 6) | (hour >= 23)).astype(int)
    lat = pd.to_numeric(df['lat'], errors='coerce')
    lon = pd.to_numeric(df['lon'], errors='coerce')
    merchant_lat = pd.to_numeric(df['merchant_lat'], errors='coerce')
    merchant_lon = pd.to_numeric(df['merchant_lon'], errors='coerce')
    dx = (merchant_lon - lon) * np.cos(np.radians((merchant_lat + lat) / 2))
    distance = 111.32 * np.hypot(dx, merchant_lat - lat)
    return pd.DataFrame({
        'log_amount': np.log1p(amount),
        'hour_sin': np.sin(2 * np.pi * hour / 24),
        'hour_cos': np.cos(2 * np.pi * hour / 24),
        'weekend': (time.dt.dayofweek >= 5).astype(int),
        'night_amount': np.log1p(amount) * night,
        'log_distance': np.log1p(distance),
        'log_population': np.log1p(population),
        'amount_per_population': amount / (population + 1),
    }).replace([np.inf, -np.inf], np.nan)


def new_model():
    pipe = make_pipeline(FunctionTransformer(run_preproc), SimpleImputer(strategy='median'), StandardScaler(), LogisticRegression(max_iter=300, random_state=42))
    return pipe
