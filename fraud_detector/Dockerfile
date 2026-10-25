FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1
ENV OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1

COPY fraud_detector/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir dill==0.3.1.1

COPY pipeline/ pipeline/
COPY fraud_detector/ fraud_detector/

CMD ["python", "-m", "fraud_detector.app.app"]
