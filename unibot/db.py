from os import environ
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///{}'.format(environ['DB_PATH']),
                       echo=False,
                       connect_args={'check_same_thread': False},
                       poolclass=StaticPool)

Session = sessionmaker(bind=engine)
