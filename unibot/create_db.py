import sqlite3
from os import environ as env

def create():
    db = sqlite3.connect(env['DB_PATH'])
    db.execute('''create table if not exists user (
        user_id int,
        chat_id int,
        first_name text,
        last_name text,
        username text,
        primary key (user_id, chat_id))''')

    db.execute('''create table if not exists user_settings (
        user_id int,
        chat_id int,
        course_id text,
        year int,
        curricula text,
        do_remind int,
        primary key (user_id, chat_id))''')
