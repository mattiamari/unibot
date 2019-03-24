import logging
import sys
from unibot import bot, create_db

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO,
                        stream=sys.stdout)
    create_db.create()
    bot.Bot().run()
