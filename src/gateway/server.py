import json
import sys

import gridfs
import pika
from auth_svc import access
from auth_svc import validate
from bson.objectid import ObjectId
from flask import Flask
from flask import request
from flask import send_file
from flask_pymongo import PyMongo
from storage import util

sys.path.append("..")

from config import settings  # noqa: E402


server = Flask("__name__")

mongo_video = PyMongo(
    server,
    uri=f"{settings.mongo_uri}:{settings.mongo_port}/videos",
)

mongo_mp3 = PyMongo(
    server,
    uri=f"{settings.mongo_uri}:{settings.mongo_port}/mp3s",
)

fs_videos = gridfs.GridFS(mongo_video.db)
fs_mp3s = gridfs.GridFS(mongo_mp3.db)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=f"{settings.rabbitmq_app_name}")
)
channel = connection.channel()


@server.route("/login", methods=["POST"])
def login():
    token, error = access.login(request)

    if not error:
        return token

    return error


@server.route("/upload", methods=["POST"])
def upload():
    access, error = validate.token(request)
    if error:
        return error

    access = json.loads(access)

    if access["admin"]:
        if (len(request.files) > 1) or (len(request.files) < 1):
            return "exactly 1 file required", 400

        for _, f in request.files.items():
            error = util.upload(
                file=f,
                gridfs_instance=fs_videos,
                channel=channel,
                access=access,
            )

            if error:
                return error

        return "success!", 200

    return "not authorised", 401


@server.route("/download", methods=["GET"])
def download():
    access, error = validate.token(request)
    if error:
        return error

    access = json.loads(access)
    if access["admin"]:
        fid_string = request.args.get("fid")
        if not fid_string:
            return "fid required", 400

        try:
            out = fs_mp3s.get(ObjectId(fid_string))
            return send_file(out, download_name=f"{fid_string}.mp3")
        except Exception as error:
            print(error)
            return "internal server error", 500

    return "not authorised", 401


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=settings.port_gateway)  # noqa: S104
