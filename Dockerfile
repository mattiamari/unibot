FROM alpine:3.9

ENV TZ=Europe/Rome

RUN apk --no-cache add \
    tzdata \
    python3 \
    py3-requests \
    git \
    py3-cffi \
    openssl \
    build-base \
    python3-dev \
    openssl-dev && \
  git clone https://github.com/python-telegram-bot/python-telegram-bot --recursive /tmp/python-telegram-bot && \
  cd /tmp/python-telegram-bot && \
  python3 setup.py install && \
  rm -rf /tmp/python-telegram-bot && \
  apk --no-cache del git build-base python3-dev openssl-dev && \
  ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /app

COPY unibot ./unibot
COPY assets ./assets
COPY start.py ./start.py

CMD ["python3", "start.py"]
