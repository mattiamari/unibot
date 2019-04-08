import logging
import sys
from os import path, environ

from alembic.config import Config
from alembic import command

from unibot.db import engine
from unibot.bot.users_model import Base


logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    stream=sys.stdout)


def db_exists():
    return path.isfile(environ['DB_PATH'])


if __name__ == '__main__':
    if not db_exists():
        logging.info('DB does not exist. Creating...')
        Base.metadata.create_all(engine)
        alembic_cfg = Config("alembic.ini")
        command.stamp(alembic_cfg, "head")
        sys.exit(0)
    logging.info('DB already exists')
