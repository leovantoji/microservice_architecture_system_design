import json
import os
import sys
import tempfile

import moviepy.editor as mp
import pika
from bson.objectid import ObjectId
from gridfs import GridFS

sys.path.append("..")

from config import settings  # noqa: E402


def start(
    message,
    fs_videos: GridFS,
    fs_mp3s: GridFS,
    channel: pika.adapters.blocking_connection.BlockingChannel,
):
    message = json.loads(message)

    # empty tempfile
    with tempfile.NamedTemporaryFile() as tf:

        # get video from gridfs
        out = fs_videos.get(ObjectId(message["video_fid"]))

        # add video content to empty file
        tf.write(out.read())

        # create audio from temp file
        audio = mp.VideoFileClip(tf.name).audio

    # write audio to the file
    tf_path = tempfile.gettempdir() + f"/{message['video_fid']}.mp3"
    audio.write_audiofile(tf_path)

    # save file to mongo
    with open(tf_path, "rb") as f:
        data = f.read()
        fid = fs_mp3s.put(data)

    # remove the temp audio file
    os.remove(tf_path)

    message["mp3_fid"] = str(fid)

    try:
        channel.basic_publish(
            exchange="",
            routing_key=settings.mp3_queue,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    except Exception:
        fs_mp3s.delete(fid)
        return "failed to publish message"
