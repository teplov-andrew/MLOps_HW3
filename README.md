# MLOps HW3

## 1. Подготовка

Установите и запустите Docker Desktop. Скачайте `train.csv`
со [страницы соревнования](https://www.kaggle.com/competitions/teta-ml-1-2025/data)
и положите его в `data/`

## 2. Запуск

```bash
docker compose up -d --build
docker compose ps -a
```

## 3. Переобучение

Откройте [Airflow](http://localhost:8081), логин и пароль — `admin`.
Запустите `add_label_batch` кнопкой start и дождитесь завершения.
Затем запустите `train_model`. Задачи и их состояния видны во вкладке Graph (если тыкнуть на train_model).

```bash
docker compose exec airflow-scheduler airflow dags list-runs -d train_model
```

## 4. Проверка результатов

После публикации в каталоге появится новый `.joblib`, а в `current.json` изменится версия:

```bash
docker compose exec fraud_detector ls -lh /opt/project/shared/models
docker compose exec fraud_detector cat /opt/project/shared/models/current.json
```

Прочитайте пять новых результатов:

```bash
docker compose exec kafka /opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server kafka:9092 --topic scores --max-messages 5 --timeout-ms 30000
```

В сообщениях должны быть `transaction_id`, `score`, `fraud_flag`, `model_version`.
Версия должна совпадать с `version` в `current.json`.

Проверьте метрики новой `new_model` и текущей `baseline` модели:

```bash
docker compose exec airflow-scheduler bash -c 'cat /opt/project/shared/runs/retrain/*/metrics.json'
```

Если результаты ещё не появились, проверьте логи:

```bash
docker compose logs --tail=50 airflow-init airflow-scheduler fraud_detector
```

## 5. Остановка

```bash
docker compose down
```
