import pika

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declare exchange & queue
channel.exchange_declare(exchange='direct_logs', exchange_type='direct')
queue_name = 'hello'
channel.queue_declare(queue=queue_name)

# Bind queue
channel.queue_bind(exchange='direct_logs', queue=queue_name, routing_key='info')

# Callback function
def callback(ch, method, properties, body):
    print(f" [x] Received {body.decode()}")

# Consume messages
channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
