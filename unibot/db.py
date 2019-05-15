from os import environ
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

conn_string = ('mysql+pymysql://{}:{}@{}/{}?charset=utf8mb4'
               .format(environ['DB_USER'],
                       environ['DB_PASS'],
                       environ['DB_HOST'],
                       environ['DB_NAME']))

engine = create_engine(conn_string,
                       echo=False,
                       pool_recycle=600, # seconds
                       pool_size=10,
                       max_overflow=5,
                       pool_timeout=5, # seconds
                       pool_pre_ping=True)

Session = sessionmaker(bind=engine)
