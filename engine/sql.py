import sqlite3
import logging


def catch_sql_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except sqlite3.Error as e:
            logging.error(f'Ошибка доступа к базе данных! Дополнительная информация: {e}')
    return wrapper


@catch_sql_exceptions
def create_tables():
    with sqlite3.connect("database/main.db") as db_connect:
        cursor = db_connect.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS letters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipient_discord_id INTEGER NOT NULL,
            recipient_username TEXT NOT NULL,
            recipient_globalname TEXT NOT NULL,
            sender_discord_id INTEGER NOT NULL,
            sender_username TEXT NOT NULL,
            sender_alias TEXT,
            body_content TEXT NOT NULL,
            image_binary_data BLOB,
            image_filename TEXT
            )""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS counter (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_discord_id INTEGER NOT NULL,
            count_letters INTEGER DEFAULT 0
            )""")


@catch_sql_exceptions
def drop_tables():
    with sqlite3.connect("database/main.db") as db_connect:
        cursor = db_connect.cursor()
        cursor.execute("DROP TABLE IF EXISTS letters")
        cursor.execute("DROP TABLE IF EXISTS counter")
        create_tables()


@catch_sql_exceptions
def add_letter_db_record(
        recipient_discord_id,
        recipient_username,
        recipient_globalname,
        sender_discord_id,
        sender_username,
        body_content,
        sender_alias=None,
        image_binary_data=None,
        image_filename=None):
    with sqlite3.connect("database/main.db") as db_connect:
        cursor = db_connect.cursor()
        cursor.execute(
            """INSERT INTO letters (
                recipient_discord_id,
                recipient_username,
                recipient_globalname,
                sender_discord_id,
                sender_username,
                sender_alias,
                body_content,
                image_binary_data,
                image_filename
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (recipient_discord_id,
             recipient_username,
             recipient_globalname,
             sender_discord_id,
             sender_username,
             sender_alias,
             body_content,
             image_binary_data,
             image_filename)
        )


@catch_sql_exceptions
def get_letter_db_record(record_id):
    with sqlite3.connect("database/main.db") as db_connect:
        cursor = db_connect.cursor()
        cursor.execute("SELECT * FROM letters WHERE id = ?",
                       (record_id,))
        return cursor.fetchone()


@catch_sql_exceptions
def delete_letter_db_record(record_id):
    with sqlite3.connect("database/main.db") as db_connect:
        cursor = db_connect.cursor()
        cursor.execute("DELETE FROM letters WHERE id = ?",
                       (record_id,))


@catch_sql_exceptions
def get_letters_by_user_db_records(sender_discord_id):
    with sqlite3.connect("database/main.db") as db_connect:
        cursor = db_connect.cursor()
        cursor.execute("SELECT * FROM letters WHERE sender_discord_id = ?",
                       (sender_discord_id,))
        for row in cursor:
            yield row


@catch_sql_exceptions
def get_letters_db_records():
    with sqlite3.connect("database/main.db") as db_connect:
        cursor = db_connect.cursor()
        cursor.execute("SELECT * FROM letters")
        for row in cursor:
            yield row


@catch_sql_exceptions
def is_letter_send_already(sender_discord_id, recipient_discord_id):
    with sqlite3.connect("database/main.db") as db_connect:
        cursor = db_connect.cursor()
        cursor.execute("SELECT * FROM letters WHERE sender_discord_id = ? AND recipient_discord_id = ?",
                       (sender_discord_id, recipient_discord_id))
        return True if cursor.fetchone() else False


@catch_sql_exceptions
def count_letters():
    with sqlite3.connect("database/main.db") as db_connect:
        cursor = db_connect.cursor()
        cursor.execute("SELECT COUNT(*) FROM letters")
        return cursor.fetchone()[0]


@catch_sql_exceptions
def get_count(sender_discord_id):
    with sqlite3.connect("database/main.db") as db_connect:
        cursor = db_connect.cursor()
        cursor.execute("SELECT count_letters FROM counter WHERE sender_discord_id = ?",
                       (sender_discord_id,))
        return cursor.fetchone()


@catch_sql_exceptions
def set_count(sender_discord_id):
    with sqlite3.connect("database/main.db") as db_connect:
        cursor = db_connect.cursor()
        cursor.execute("INSERT INTO counter (sender_discord_id, count_letters) VALUES (?, ?)",
                       (sender_discord_id, 0))
        return cursor.fetchone()


@catch_sql_exceptions
def increment_count(sender_discord_id):
    with sqlite3.connect("database/main.db") as db_connect:
        cursor = db_connect.cursor()
        cursor.execute("UPDATE counter SET count_letters = count_letters + 1 WHERE sender_discord_id = ?",
                       (sender_discord_id,))


@catch_sql_exceptions
def decrement_count(sender_discord_id):
    with sqlite3.connect("database/main.db") as db_connect:
        cursor = db_connect.cursor()
        cursor.execute("UPDATE counter SET count_letters = count_letters - 1 WHERE sender_discord_id = ?",
                       (sender_discord_id,))
