import logging
import sys
import os
from datetime import datetime, time
from unibot import bot, db

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        level=logging.INFO,
                        stream=sys.stdout)
    mode = 'Testing' if os.environ['TESTING'] == '1' else 'Production'

    logging.info("Starting UniBot version {}".format(os.environ['BOT_VERSION']))
    logging.info("Current mode is {}".format(mode))
    logging.info('Server time is {}'.format(datetime.now()))

    db.migrate()
    bot.Bot().run()
