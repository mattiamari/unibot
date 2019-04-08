#!/bin/sh

python3 createdb.py && \
    alembic upgrade head && \
    python3 start.py
