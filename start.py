import logging
import sys
import os
from datetime import datetime
from time import sleep
import pymysql.cursors
from unibot.bot import bot


def db_available():
    try:
        pymysql.connect(host=os.environ['DB_HOST'],
                        user=os.environ['DB_USER'],
                        password=os.environ['DB_PASS'],
                        db=os.environ['DB_NAME'],
                        charset='utf8mb4',
                        cursorclass=pymysql.cursors.DictCursor)
        return True
    except Exception:
        return False


def main():
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        level=logging.INFO,
                        stream=sys.stdout)
    mode = 'Testing' if os.environ['TESTING'] == '1' else 'Production'

    while not db_available():
        logging.info('Waiting for DB...')
        sleep(3)

    logging.info("Starting UniBot version %s", os.environ['BOT_VERSION'])
    logging.info("Current mode is %s", mode)
    logging.info('Server time is %s', datetime.now())

    bot.Bot().run()


if __name__ == '__main__':
    main()
