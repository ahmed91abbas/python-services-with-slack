import time
import re
import sqlite3
from sqlite3 import Error
import datetime

TABLE_NAME = "reminders"
ID_COL = "generated_id"
TEXT_COL = "text"
CREATED_COL = "created_datetime"
SCHEDULED_COL = "scheduled_datetime"

class Reminder:

    def __init__(self, db_file):
        self.sec_names = ["s", "sec", "second", "seconds"]
        self.min_names = ["m", "min", "minute", "minutes"]
        self.hour_names = ["h", "hour", "hours"]

        self.conn = self.create_connection(db_file)

    def create_connection(self, db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Error as e:
            print(str(e))
        return conn

    def create_task(self, text, delta):
        with self.conn:
            cur = self.conn.cursor()
            sql = f'''INSERT INTO {TABLE_NAME}
                    ({TEXT_COL}, {CREATED_COL}, {SCHEDULED_COL})
                    VALUES (?,?,?)'''
            created_datetime = datetime.datetime.now()
            scheduled_datetime = created_datetime + datetime.timedelta(0,delta)
            cur.execute(sql, (text, created_datetime, scheduled_datetime))
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
            print(str(e))
            return None
        return None

    def delete_all_reminders(self):
        sql = f'DELETE FROM {TABLE_NAME}'
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()
        cur.close()
        return cur.rowcount

    def list_all_reminders(self):
        with self.conn:
            cur = self.conn.cursor()
            cur.execute(f"SELECT * FROM {TABLE_NAME}")
            rows = cur.fetchall()
        return rows

    def build_cond_re(self, elements):
        res = ""
        for i in range(len(elements)-1):
            res += elements[i] + "|"
        res += elements[len(elements)-1]
        return res

    def convert_to_sec(self, number, unit):
        if unit in self.sec_names:
            return number
        if unit in self.min_names:
            return number * 60
        if unit in self.hour_names:
            return number * 3600

    def parse_message(self, message):
        cond_re = self.build_cond_re(self.sec_names + self.min_names + self.hour_names)
        list_all_regex = "(?:show |list )?(?:all )?reminders$"
        after_regex = f'(?:reminder|remind me) to (.*) after (\\d+) ({cond_re})$'

        text = None
        delta = None
        m = self.get_match(after_regex, message)
        if m:
            text = m.group(1)
            number = int(m.group(2))
            unit = m.group(3)
            delta = self.convert_to_sec(number, unit)
            return text, delta

        m = self.get_match(list_all_regex, message)
        if m:
            results = self.list_all_reminders()
            return results, None

        return text, delta

    def get_match(self, regex, text):
        p = re.compile(regex, re.IGNORECASE)
        return p.match(text)

    def build_response_message(self, message, from_channel=None, to_channel=None):
        text, delta = self.parse_message(message)
        if delta:
            task_id = self.create_task(text, delta)
            time.sleep(delta)
            self.delete_task(task_id)
            return "Reminder: " + text, to_channel
        elif type(text) is list:
            if text:
                response_message = self.init_message()
                for elem in text:
                    response_message["blocks"].append(\
                        self.create_message_section(elem))
                return response_message, from_channel
            else:
                return "Nothing scheduled.", from_channel
        else:
            return "Failed to parse reminder message", from_channel

    def init_message(self):
        message = {}
        message["blocks"] = []
        return message

    def create_message_section(self, elements):
        section = {}
        section["type"] = "section"
        section["text"] = {}
        section["text"]["type"] = "mrkdwn"

        text = elements[1]
        scheduled_ts = elements[3]

        scheduled_ts = datetime.datetime.strptime(scheduled_ts, '%Y-%m-%d %H:%M:%S.%f')
        scheduled_ts = scheduled_ts.strftime("%Y-%m-%d %H:%M:%S")

        section["text"]["text"] = f"*{text}* - Scheduled at: *{scheduled_ts}*"
        return section

if __name__ == '__main__':
    message = "reminder to x and y after 7 sec"
    Reminder("../db/services_db.db").build_response_message(message)