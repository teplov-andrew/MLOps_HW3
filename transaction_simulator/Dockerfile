FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

COPY transaction_simulator/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY transaction_simulator/ transaction_simulator/

CMD ["python", "-m", "transaction_simulator.app"]
