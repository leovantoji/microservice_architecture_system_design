ARG PY_VERSION

FROM python:${PY_VERSION}-slim-bullseye

ARG PORT
ARG DOCKER_ACCOUNT

RUN apt-get update \
    && apt-get install -y --no-install-recommends --no-install-suggests \
    build-essential gettext-base \
    && pip install --no-cache-dir --upgrade pip

WORKDIR /app
ARG APP_LOCAL_PATH
COPY ${APP_LOCAL_PATH}/requirements.txt /app

RUN pip install --no-cache-dir -r /app/requirements.txt
COPY ${APP_LOCAL_PATH} /app

COPY src/config.py /app
COPY .env /app

EXPOSE ${PORT}

CMD ["python3", "server.py"]
