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
        self.error_msg = None
        self.conn = self.create_connection(db_file)

    def init_action_list(self):
        action_list = {}

        action_list["add_task"] = {}
        action_list["add_task"]["regex"] = 'add (.*) to todo'
        action_list["add_task"]["function"] = self.create_task
        action_list["add_task"]["success_message"] = \
            "Created a new task with ID %s"
        action_list["add_task"]["failed_message"] = \
            "Failed to create a new task"

        action_list["enumerate_all"] = {}
        action_list["enumerate_all"]["regex"] = '(?:enumerate |list |show |all )?todo'
        action_list["enumerate_all"]["function"] = self.list_all_tasks
        action_list["enumerate_all"]["success_message"] = \
            "All tasks in Todo list:"
        action_list["enumerate_all"]["failed_message"] = \
            "Nothing to show. Todo list is empty."

        action_list["delete_task"] = {}
        action_list["delete_task"]["regex"] = 'delete (\\d+) from todo'
        action_list["delete_task"]["function"] = self.delete_task
        action_list["delete_task"]["success_message"] = \
            "The task with ID %s has been removed successfully"
        action_list["delete_task"]["failed_message"] = \
            "Failed to remove the task"

        action_list["delete_all"] = {}
        action_list["delete_all"]["regex"] = 'delete (?:all|everything) from todo'
        action_list["delete_all"]["function"] = self.delete_all_tasks
        action_list["delete_all"]["success_message"] = \
            "Deleted %s tasks. Todo list is empty now."
        action_list["delete_all"]["failed_message"] = \
            "Nothing to remove.Todo list is empty."

        return action_list

    def create_connection(self, db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Error as e:
            self.error_msg = str(e)
        return conn

    def list_all_tasks(self):
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
            if cur.rowcount:
                return task_id
        except Error as e:
            self.error_msg = str(e)
            print(str(e))
            return None
        return None

    def delete_all_tasks(self):
        sql = f'DELETE FROM {TABLE_NAME}'
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()
        cur.close()
        return cur.rowcount

    def excute_message_action(self, message):
        for action in self.action_list:
            p = re.compile(self.action_list[action]["regex"], re.IGNORECASE)
            m = p.match(message)
            if m:
                try:
                    text = m.group(1)
                except:
                    text = None

                if text:
                    return self.action_list[action],\
                        self.action_list[action]["function"](text)
                else:
                    return self.action_list[action],\
                        self.action_list[action]["function"]()
        failed = {}
        failed["failed_message"] = "Command not found!"
        return failed, None

    def build_response_message(self, message_text):

        action, results = self.excute_message_action(message_text)

        if self.error_msg:
            return self.error_msg

        response_message = self.init_message()

        if not results:
            response_message["blocks"].append(self.create_title_section(\
                action["failed_message"]))
            return response_message

        if type(results) is list:
            response_message["blocks"].append(self.create_title_section(\
                action["success_message"]))
            for res in results:
                response_message["blocks"].append(\
                    self.create_title_section(res))
        else:
            response_message["blocks"].append(self.create_title_section(\
                action["success_message"] % results))

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
    message = "delete everything from todo"
    message = "add test to todo"
    message = "delete 2 from todo"
    message = "enumerate todo"
    res = todo_list.build_response_message(message)
    for section in res["blocks"]:
        print(section["text"]["text"])