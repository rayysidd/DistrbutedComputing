import pika, time

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declare durable exchange & queue
channel.exchange_declare(exchange='math_operations', exchange_type='direct', durable=True)
channel.queue_declare(queue='addition_queue', durable=True)

n = 1
try:
    while True:
        message = f"{n} + {n+1}"
        channel.basic_publish(exchange='math_operations', routing_key='addition', body=message)
        print(f" [x] Sent: {message}")
        n += 1
        time.sleep(2)
except KeyboardInterrupt:
    print("Producer stopped.")
connection.close()
