from faststream.rabbit import RabbitQueue


payments_new_queue = RabbitQueue(name="payments.new", durable=True)
