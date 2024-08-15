import sqlite3
import os
from contextlib import closing
from loguru import logger
from redcapconnector.config.log_config import handlers

# setting up the logging
logger.configure(
    handlers=handlers,
)

db_dir = os.path.join(os.path.dirname(__file__), "data", "result_json.db")


@logger.catch
def create_db_table():
    global con
    try:
        # create connection and database
        con = sqlite3.Connection(db_dir)

        # create cursor to execute SQL statement
        cur = con.cursor()

        # SQL statement to CREATE TABLE
        sql_create_table = """
            CREATE TABLE IF NOT EXISTS results(
              datetime DATETIME,
              project TEXT,
              message BLOB,
            );
        """

        # execute sql statement
        cur.execute(sql_create_table)

        # commit the transaction
        con.commit()

        cur.close()
    # except sqlite3.Error as e:
    #    print(f'An error occurred while creating database table: {e.sqlite_errorcode} - {e.sqlite_errorname}')
    finally:
        con.close()


@logger.catch
def insert_record(t_date, t_project, t_message):
    global con
    try:

        # create connection and database
        con = sqlite3.Connection(db_dir)

        # create cursor to execute SQL statement
        cur = con.cursor()

        # sql INSERT statement
        sql_insert = f'INSERT INTO transactions(datetime,analyzer, message) VALUES(?,?,?);'

        cur.execute(sql_insert, (t_date, t_project, t_message))

        con.commit()

        cur.close()

    # except sqlite3.Error as e:
    #    print(f'An error occurred while inserting record into table: {e.sqlite_errorcode} {e}')
    finally:
        con.close()


if __name__ == '__main__':
    create_db_table()
