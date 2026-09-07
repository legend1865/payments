# Payments processing service

Асинхронный сервис обработки платежей. API сохраняет платёж и событие в outbox в одной транзакции. Отдельный publisher переносит события из outbox в RabbitMQ, после чего consumer эмулирует обработку платежа, обновляет его статус и отправляет webhook.

## Стек

- Python 3.12
- FastAPI и Pydantic v2
- SQLAlchemy 2.0 в асинхронном режиме
- PostgreSQL
- RabbitMQ и FastStream
- Alembic
- Docker Compose

## Запуск

Создайте файл `.env` из примера:

```bash
cp .env.example .env
```

На Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

При необходимости измените `API_KEY`, пароли PostgreSQL и RabbitMQ в `.env`, затем запустите сервисы:

```bash
docker compose up --build -d
```

Будут запущены:

- `api` — HTTP API на `http://localhost:8000`;
- `outbox-publisher` — публикация событий из outbox;
- `consumer` — обработка платежей и отправка webhook;
- `postgres` — PostgreSQL на порту `5432`;
- `rabbitmq` — RabbitMQ на порту `5672`, Management UI на `http://localhost:15672`.

Миграции Alembic применяются автоматически перед запуском API. Swagger доступен по адресу `http://localhost:8000/docs`.

Просмотр состояния и логов:

```bash
docker compose ps
docker compose logs -f api outbox-publisher consumer
```

Остановка:

```bash
docker compose down
```

Для удаления созданных Docker volumes вместе с данными:

```bash
docker compose down -v
```

## API

Все API-эндпоинты требуют статический ключ из переменной `API_KEY` в заголовке `X-API-Key`.

### Создание платежа

```http
POST /api/v1/payments
```

Пример запроса:

```bash
curl -X POST http://localhost:8000/api/v1/payments \
  -H "Content-Type: application/json" \
  -H "X-API-Key: change-me" \
  -H "Idempotency-Key: payment-order-1001" \
  -d '{
    "amount": "1500.50",
    "currency": "RUB",
    "description": "Order 1001",
    "metadata": {"order_id": 1001},
    "webhook_url": "https://client.example.com/payment-webhook"
  }'
```

Успешный ответ имеет статус `202 Accepted`:

```json
{
  "payment_id": "87dc19be-6174-44a9-a90d-dbc34e91936f",
  "status": "pending",
  "created_at": "2026-09-04T12:00:00Z"
}
```

Повторный запрос с тем же `Idempotency-Key` возвращает ранее созданный платёж и не создаёт повторную запись или событие outbox.

### Получение платежа

```http
GET /api/v1/payments/{payment_id}
```

Пример запроса:

```bash
curl http://localhost:8000/api/v1/payments/87dc19be-6174-44a9-a90d-dbc34e91936f \
  -H "X-API-Key: change-me"
```

Пример ответа:

```json
{
  "payment_id": "87dc19be-6174-44a9-a90d-dbc34e91936f",
  "amount": "1500.50",
  "currency": "RUB",
  "description": "Order 1001",
  "metadata": {"order_id": 1001},
  "status": "succeeded",
  "idempotency_key": "payment-order-1001",
  "webhook_url": "https://client.example.com/payment-webhook",
  "created_at": "2026-09-04T12:00:00Z",
  "processed_at": "2026-09-04T12:00:04Z"
}
```

## Обработка платежей

При создании платежа записи в таблицах `payments` и `outbox` сохраняются атомарно. Outbox publisher читает неопубликованные события и отправляет их в очередь `payments.new`, после чего помечает записи как опубликованные.

Consumer выполняет один обработчик:

1. Эмулирует обработку в течение 2–5 секунд.
2. Устанавливает статус `succeeded` с вероятностью 90% или `failed` с вероятностью 10%.
3. Сохраняет статус и время обработки в PostgreSQL.
4. Отправляет `POST` на указанный `webhook_url`.

Тело webhook:

```json
{
  "payment_id": "87dc19be-6174-44a9-a90d-dbc34e91936f",
  "status": "succeeded",
  "processed_at": "2026-09-04T12:00:04+00:00"
}
```

Если webhook или обработка завершается ошибкой, сообщение повторно поступает через очередь `payments.new.retry`. Выполняется не более трёх попыток с экспоненциальными задержками. После последней неудачи сообщение публикуется в `payments.new.dlq`.

## Локальная проверка кода

```bash
uv sync
uv run ruff check .
uv run ruff format --check .
```
