import logging
import sqlite3
import json
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
    'query': "alter table user_settings add column deleted int default 0;"
})

migrations.append({
    'seq': 2,
    'desc': 'add remind_time colummn to user_settings',
    'query': "alter table user_settings add column remind_time text;"
})

migrations.append({
    'seq': 3,
    'desc': 'set default remind_time',
    'query': "update user_settings set remind_time='7:30' where do_remind=1;"
})

migrations.append({
    'seq': 4,
    'desc': 'delete settings for groups with more than one config',
    'query': ("delete from user_settings where chat_id in "
              "(select chat_id as cnt from user_settings group by chat_id having count(*) > 1);")
})

migrations.append({
    'seq': 5,
    'desc': 'create new user_settings table',
    'query': """create table if not exists user_settings_new (
        user_id int,
        chat_id int,
        course_id text,
        year int,
        curricula text,
        do_remind int default 0,
        remind_time text,
        deleted int default 0,
        primary key (chat_id));"""
})

migrations.append({
    'seq': 6,
    'desc': 'migrate data to the new user_settings table, cleaning deleted',
    'query': ("insert into user_settings_new (user_id, chat_id, course_id, year, curricula, do_remind, remind_time, deleted) "
              "select user_id, chat_id, course_id, year, curricula, do_remind, remind_time, deleted from user_settings where deleted=0;")
})

migrations.append({
    'seq': 7,
    'desc': 'delete old user_settings table',
    'query': ("drop table user_settings; "
              "alter table user_settings_new rename to user_settings;")
})

migrations.append({
    'seq': 8,
    'desc': 'update remind_time to full time string',
    'query': "update user_settings set remind_time = remind_time || ':00.000000' where remind_time is not null and remind_time != ''"
})


def migrate():
    logging.info('Applying migrations')
    db = sqlite3.connect(environ['DB_PATH'])
    migrations.sort(key=lambda e: e['seq'])
    for m in migrations:
        if m['seq'] in applied_migrations:
            logging.info("* SKIPPED '%s'", m['desc'])
            continue
        if m['query'] is not None:
            apply(db=db, seq=m['seq'], desc=m['desc'], query=m['query'])
    save_applied()
    db.close()


def apply(db, seq, desc, query):
    logging.info("* applying '%s'", desc)
    try:
        db.executescript(query)
        db.commit()
        applied_migrations.append(seq)
    except Exception as e:
        logging.exception(e)
        sys.exit(1)


def save_applied():
    with open(applied_migrations_file, 'w') as fp:
        json.dump(applied_migrations, fp)
