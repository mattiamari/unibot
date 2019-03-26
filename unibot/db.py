import sqlite3
import json
import logging
import sys
from os import environ, path

applied_migrations = []
applied_migrations_file = path.join(path.dirname(environ['DB_PATH']), 'applied_migrations.json')
if path.isfile(applied_migrations_file):
    with open(applied_migrations_file, 'r') as f:
        applied_migrations = json.load(f)

migrations = []

initial_db_query = '''create table if not exists user (
    user_id int,
    chat_id int,
    first_name text,
    last_name text,
    username text,
    primary key (user_id, chat_id));

    create table if not exists user_settings (
        user_id int,
        chat_id int,
        course_id text,
        year int,
        curricula text,
        do_remind int,
        primary key (user_id, chat_id));'''

migrations.append({
    'seq': 0,
    'desc': 'create db',
    'query': initial_db_query
})

migrations.append({
    'seq': 1,
    'desc': 'add deleted colummn to user_settings',
    'query': "alter table user_settings add column deleted int default 0"
})

def migrate():
    logging.info('Applying migrations')
    db = sqlite3.connect(environ['DB_PATH'])
    migrations.sort(key=lambda e: e['seq'])
    for m in migrations:
        if m['seq'] in applied_migrations:
            logging.info("* SKIPPED '{}'".format(m['desc']))
            continue
        apply(db=db, seq=m['seq'], desc=m['desc'], query=m['query'])
    save_applied()
    db.close()

def apply(db, seq, desc, query):
    logging.info("* applying '{}'".format(desc))
    try:
        db.executescript(query)
        db.commit()
        applied_migrations.append(seq)
    except Exception as e:
        logging.critical(e)
        sys.exit(1)

def save_applied():
    with open(applied_migrations_file, 'w') as f:
        json.dump(applied_migrations, f)
