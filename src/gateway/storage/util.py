import json

import pika


def upload(file, gridfs_instance, channel, access):
    # put the file to MongoDB
    try:
        fid = gridfs_instance.put(file)
    except Exception:
        return "internal server error", 500

    message = {
        "video_fid": str(fid),
        "mp3_fid": None,
        "username": access["username"],
    }

    # put the message on the queue using the basic exchange (empty string)
    try:
        channel.basic_publish(
            exchange="",
            routing_key="video",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
            ),
        )
    except Exception:
        gridfs_instance.delete(fid)
        return "internal server error", 500
