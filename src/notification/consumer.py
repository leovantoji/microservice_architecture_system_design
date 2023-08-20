import os
import sys

import pika
from config import settings
from send import email


def main():
    # rabbimq connection
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=f"{settings.rabbitmq_app_name}",
        )
    )
    channel = connection.channel()

    def callback(channel, method, properties, body):
        error = email.notification(body)
        if error:
            channel.basic_nack(delivery_tag=method.delivery_tag)
        else:
            channel.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=settings.mp3_queue,
        on_message_callback=callback,
    )

    print("Waiting for messages. To exit press CTRL+C")

    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted!")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
