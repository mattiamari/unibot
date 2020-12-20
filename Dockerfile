FROM alpine:3.12

ENV TZ=Europe/Rome

RUN apk --no-cache add \
    tzdata \
    python3 \
    py3-requests \
    git \
    py3-cffi \
    openssl \
    build-base \
    py3-pip \
    libffi-dev \
    python3-dev \
    openssl-dev && \
  python3 -m pip install beautifulsoup4 sqlalchemy alembic pymysql python-telegram-bot && \
  apk --no-cache del git build-base python3-dev openssl-dev && \
  ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /app

COPY . ./

ENV PYTHONPATH=/app
CMD ["python3", "start.py"]
