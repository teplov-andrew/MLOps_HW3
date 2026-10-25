FROM apache/airflow:2.10.5-python3.11

WORKDIR /opt/project

COPY airflow/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir "apache-airflow==2.10.5" -r /tmp/requirements.txt

COPY --chown=airflow:root pipeline/ pipeline/
COPY --chown=airflow:root fraud_detector/ fraud_detector/
COPY --chown=airflow:root dags/ /opt/airflow/dags/

ENV PYTHONPATH=/opt/project
ENV OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
