import pika

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declare direct exchange
channel.exchange_declare(exchange='direct_logs', exchange_type='direct')

# Declare queue
queue_name = 'hello'
channel.queue_declare(queue=queue_name)

# Bind queue to exchange
channel.queue_bind(exchange='direct_logs', queue=queue_name, routing_key='info')

# Publish message
message = 'Hello, RabbitMQ!'
channel.basic_publish(exchange='direct_logs', routing_key='info', body=message)

print(f" [x] Sent '{message}'")
connection.close()
