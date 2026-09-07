from faststream.rabbit import RabbitQueue


payments_new_queue = RabbitQueue(name="payments.new", durable=True)
payments_retry_queue = RabbitQueue(
    name="payments.new.retry",
    durable=True,
    arguments={
        "x-dead-letter-exchange": "",
        "x-dead-letter-routing-key": payments_new_queue.name,
    },
)
payments_dlq_queue = RabbitQueue(name="payments.new.dlq", durable=True)
