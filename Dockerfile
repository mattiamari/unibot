FROM alpine:3.9

RUN apk --no-cache add \
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
  apk --no-cache del git build-base python3-dev openssl-dev

WORKDIR /app

COPY bot/ .

CMD ["python3", "bot.py"]
