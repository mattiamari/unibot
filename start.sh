#!/bin/sh

alembic upgrade head && python3 start.py
