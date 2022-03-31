#!/usr/bin/env python
# -*- coding: utf-8 -*-
#!/usr/bin/env python
import pika
import sys

# connection = pika.BlockingConnection(
#     pika.ConnectionParameters(host='localhost'))
# channel = connection.channel()
credentials = pika.PlainCredentials('admin', 'admin')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='172.31.236.43', port=5672, virtual_host='/', credentials=credentials))
channel = connection.channel()
channel.queue_declare(queue='task_queue', durable=True)

channel.exchange_declare(exchange='direct_logs', exchange_type='direct')

severity = sys.argv[1] if len(sys.argv) > 1 else 'info'
message = ' '.join(sys.argv[2:]) or 'Hello World!'

channel.basic_publish(
    exchange='direct_logs', routing_key=severity, body=message)
print(" [x] Sent %r:%r" % (severity, message))

connection.close()