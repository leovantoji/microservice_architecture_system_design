import json
import sys

import gridfs
import pika
from auth import validate
from auth_svc import access
from flask import Flask
from flask import request
from flask_pymongo import PyMongo
from storage import util

sys.path.append("..")

from config import settings  # noqa: E402


server = Flask("__name__")
server.config["MONGO_URI"] = f"{settings.mongo_uri}:{settings.mongo_port}/videos"

mongo = PyMongo(server)

fs = gridfs.GridFS(mongo.db)

connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
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
    access = json.loads(access)

    if access["admin"]:
        if (len(request.files) > 1) or (len(request.files) < 1):
            return "exactly 1 file required", 400

        for _, f in request.files.items():
            error = util.upload(
                file=f,
                gridfs_instance=fs,
                channel=channel,
                access=access,
            )

            if error:
                return error

        return "success!", 200

    return "not authorised", 401


@server.route("/download", methods=["GET"])
def download():
    pass


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=settings.port_gateway)  # noqa: S104
