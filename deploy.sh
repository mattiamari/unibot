#!/bin/bash

git clean -dfx && \
    git reset --hard master && \
    git pull && \
    sudo docker-compose up --build -d
