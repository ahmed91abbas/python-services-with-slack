import sqlite3
from sqlite3 import Error
from datetime import datetime
import re

TABLE_NAME = "todo_list"
ID_COL = "generated_id"
TEXT_COL = "text"
CREATED_COL = "created_datetime"

class Todo_list:

    def __init__(self, db_file):
        self.action_list = self.init_action_list()
        self.add_regex = 'add (.*) to todo(?:_list)?'
        self.error_msg = None
        self.conn = self.create_connection(db_file)

    def init_action_list(self):
        action_list = {}

        action_list["add"] = {}
        action_list["add"]["regex"] = 'add (.*) to todo(?:_list)?'
        action_list["add"]["success_message"] = \
            "Created a new task with ID: "
        action_list["add"]["failed_message"] = \
            "Failed to create a new task"

        return action_list

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

    def delete_task(self, task_id):
        try:
            cur = self.conn.cursor()
            sql = f'''DELETE FROM {TABLE_NAME} WHERE {ID_COL} = ?'''
            cur.execute(sql, (task_id, ))
            self.conn.commit()
            cur.close()
        except Error as e:
            self.error_msg = str(e)
            print(str(e))

    def delete_all_tasks(self):
        sql = f'DELETE FROM {TABLE_NAME}'
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()
        cur.close()

    def excute_message_action(self, message):
        for action in self.action_list:
            p = re.compile(self.action_list[action]["regex"], re.IGNORECASE)
            m = p.match(message)
            if m:
                text = m.group(1)
                return self.action_list[action], self.create_task(text)

    def build_response_message(self, message_text):

        action, results = self.excute_message_action(message_text)

        if self.error_msg:
            return self.error_msg

        response_message = self.init_message()

        if not results:
            response_message["blocks"].append(self.create_title_section(\
                action["failed_message"]))
            return response_message

        response_message["blocks"].append(self.create_title_section(\
            action["success_message"]))
        response_message["blocks"].append(self.create_title_section(\
            f"{results}"))

        return response_message

    def init_message(self):
        message = {}
        message["blocks"] = []
        return message

    def create_title_section(self, text):
        section = {}
        section["type"] = "section"
        section["text"] = {}
        section["text"]["type"] = "plain_text"
        section["text"]["text"] = text
        return section

if __name__ == '__main__':
    todo_list = Todo_list("../db/information_bot.db")
    message = "add xdsad dasdsa to todo"
    res = todo_list.build_response_message(message)
    for section in res["blocks"]:
        print(section["text"]["text"])