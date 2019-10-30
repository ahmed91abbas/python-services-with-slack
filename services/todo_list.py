import sqlite3
from sqlite3 import Error
from datetime import datetime

TABLE_NAME = "todo_list"
ID_COL = "generated_id"
TEXT_COL = "text"
CREATED_COL = "created_datetime"

class Todo_list:

    def __init__(self, db_file):
        self.error_msg = None
        self.conn = self.create_connection(db_file)

    def create_connection(self, db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Error as e:
            self.error_msg = str(e)
        return conn

    def select_all(self):
        with self.conn:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM todo_list")
            rows = cur.fetchall()
        return rows

    def create_task(self, text):
        with self.conn:
            cur = self.conn.cursor()
            sql = f'''INSERT INTO {TABLE_NAME}
                    ({TEXT_COL}, {CREATED_COL})
                    VALUES (?,?)'''
            cur.execute(sql, (text, datetime.now()))
        return cur.lastrowid

    def remove_task(self, task_id):
        try:
            cur = self.conn.cursor()
            sql = f'''DELETE FROM {TABLE_NAME} WHERE {ID_COL} = ?'''
            cur.execute(sql, (task_id, ))
            self.conn.commit()
            cur.close()
        except Error as e:
            self.error_msg = str(e)
            print(str(e))

if __name__ == '__main__':
    todo_list = Todo_list("../db/information_bot.db")
    res = todo_list.create_task("test2")
    todo_list.remove_task(1)
    rows = todo_list.select_all()
    for row in rows:
        print(row)