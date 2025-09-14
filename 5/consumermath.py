import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='math_operations', exchange_type='direct', durable=True)
channel.queue_declare(queue='addition_queue', durable=True)
channel.queue_bind(exchange='math_operations', queue='addition_queue', routing_key='addition')

def callback(ch, method, properties, body):
    message = body.decode()
    num1, num2 = map(int, message.split(' + '))
    print(f" [x] Received: {message} = {num1 + num2}")

channel.basic_consume(queue='addition_queue', on_message_callback=callback, auto_ack=True)
print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
