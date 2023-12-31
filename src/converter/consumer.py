import os
import sys

import gridfs
import pika
from config import settings
from convert import to_mp3
from pymongo import MongoClient


def main():
    client = MongoClient(f"{settings.mysql_host}", settings.mongo_port)
    db_videos = client.videos
    db_mp3s = client.mp3s

    # gridfs
    fs_videos = gridfs.GridFS(db_videos)
    fs_mp3s = gridfs.GridFS(db_mp3s)

    # rabbimq connection
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host="rabbitmq",
        )
    )
    channel = connection.channel()

    def callback(channel, method, properties, body):
        error = to_mp3.start(body, fs_videos, fs_mp3s, channel)
        if error:
            channel.basic_nack(delivery_tag=method.delivery_tag)
        else:
            channel.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=settings.video_queue,
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
