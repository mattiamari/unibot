import logging
import sys
from time import sleep
from os import environ

import pymysql.cursors
from alembic.config import Config
from alembic import command

from unibot.db import engine, conn_string
from unibot.bot.users_model import Base


logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    stream=sys.stdout)


def db_available():
    try:
        pymysql.connect(host=environ['DB_HOST'],
                        user=environ['DB_USER'],
                        password=environ['DB_PASS'],
                        db=environ['DB_NAME'],
                        charset='utf8mb4',
                        cursorclass=pymysql.cursors.DictCursor)
        return True
    except Exception:
        return False


if __name__ == '__main__':
    while not db_available():
        logging.info('Waiting for DB...')
        sleep(2)
    logging.info('Initializing DB...')
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option('sqlalchemy.url', conn_string)
    Base.metadata.create_all(engine)
    command.stamp(alembic_cfg, "head")
    sys.exit(0)
