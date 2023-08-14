from datetime import datetime
from datetime import timedelta

import jwt
from config import settings
from flask import Flask
from flask import request
from flask_mysqldb import MySQL


server = Flask(__name__)
mysql = MySQL(server)


@server.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    if not auth:
        return "missing credentials", 401

    # check db for username and password
    cursor = mysql.connection.cursor()
    res = cursor.execute(
        """
        SELECT
            email,
            password
        FROM
            user
        WHERE
            email=%s
        """,
        (auth.username,),
    )

    if res > 0:
        user_row = cursor.fetchone()
        email = user_row[0]
        password = user_row[1]

        if (auth.username != email) or (auth.password != password):
            return "invalid credentials", 401
        else:
            return create_jwt(auth.username, settings.jwt_secret, True)
    else:
        return "user not exist", 404


@server.route("/validate", methods=["POST"])
def validate():
    encoded_jwt = request.headers["Authorization"]

    if not encoded_jwt:
        return "missing credentials", 401

    encoded_jwt = encoded_jwt.split(" ")[1]
    try:
        decoded = jwt.decode(
            jwt=encoded_jwt, key=settings.jwt_secret, algorithm=[settings.algorithm]
        )
    except Exception:
        return "not authorised", 403

    return decoded, 200


def create_jwt(username, secret, authz: bool):
    """
    function to create jwt token

    Parameters
    ----------
    username: str
        username
    secret: str
        secret
    authz: bool
        whether the user is an admin

    Returns
    -------
    str:
        jwt token
    """
    return jwt.encode(
        payload={
            "username": username,
            "exp": datetime.utcnow()
            + timedelta(minutes=settings.access_token_expire_minutes),
            "iat": datetime.utcnow(),
            "admin": authz,
        },
        key=secret,
        algorithm=settings.algorithm,
    )


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=settings.auth_port)  # noqa: S104
