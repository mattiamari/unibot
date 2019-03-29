import logging
import sys
import os
from datetime import datetime
from unibot.bot import bot, db


def main():
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        level=logging.INFO,
                        stream=sys.stdout)
    mode = 'Testing' if os.environ['TESTING'] == '1' else 'Production'

    logging.info("Starting UniBot version %s", os.environ['BOT_VERSION'])
    logging.info("Current mode is %s", mode)
    logging.info('Server time is %s', datetime.now())

    db.migrate()
    bot.Bot().run()


if __name__ == '__main__':
    main()
