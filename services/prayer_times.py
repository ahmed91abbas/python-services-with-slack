import sqlite3
from sqlite3 import Error
import re
import time

class Prayer_times:

    def __init__(self, db_file):
        self.regex = 'prayer times(?: month| m)? (\d{2})(?: day (\d{2})| d (\d{2})| (\d{2}))?'
        self.error_msg = None
        self.conn = self.create_connection(db_file)
        try:
            self.conn = sqlite3.connect(db_file)
        except Error as e:
            self.error_msg = str(e)

    def create_connection(self, db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Error as e:
            print(e)

        return conn

    def select_time_by_date(self, month_str=None, day_str=None):
        cur = self.conn.cursor()
        if month_str and day_str:
            cur.execute("SELECT day, fajr, sunrise, dhuhr, asr, maghrib, isha \
                FROM prayer_times WHERE month=? AND day=?", (month_str, day_str,))
        elif month_str:
            cur.execute("SELECT day, fajr, sunrise, dhuhr, asr, maghrib, isha \
                FROM prayer_times WHERE month=?", (month_str,))
        else:
            return []

        rows = cur.fetchall()

        return rows

    def apply_DST_end(self, rows):
        res_rows = []
        for row in rows:
            res_row = []
            res_row.append(row[0])
            for i in range(1, len(row)):
                e = row[i]
                res_row.append(e[0] + \
                    str(int(e[1])-1) + e[2:])
            res_rows.append(res_row)
        return res_rows

    def parse_message(self, message):
        localtime = time.localtime()
        p = re.compile(self.regex, re.IGNORECASE)
        m = p.match(message)
        month = None
        day = None
        if m:
            month = m.group(1)
            for i in range(2, 5):
                if m.group(i):
                    day = m.group(i)
        else:
            month = format(localtime.tm_mon, '02')
            day = format(localtime.tm_mday, '02')

        is_dst = time.localtime().tm_isdst

        return month, day, is_dst

    def build_response_message(self, message_text):
        if self.error_msg:
            return self.error_msg

        month, day, is_dst = self.parse_message(message_text)

        rows = self.select_time_by_date(month_str=month, day_str=day)

        if month == "10" and not is_dst:
            rows = self.apply_DST_end(rows)

        response_message = self.inti_message()
        for row in rows:
            response_message["blocks"].append(\
                self.create_message_section(row))

        return response_message

    def inti_message(self):
        message = {}
        message["blocks"] = []
        return message

    def create_message_section(self, elements):
        section = {}
        section["type"] = "section"
        section["text"] = {}
        section["text"]["type"] = "mrkdwn"
        text = ""
        switch = True
        for i in range(len(elements)-1):
            if switch:
                text += elements[i] + " - "
                switch = False
            else:
                text += "*" + elements[i] + "* - "
                switch = True
        if switch:
            text += elements[i]
        else:
            text += "*" + elements[i] + "*"

        print(text)

        section["text"]["text"] = text
        return section


if __name__ == '__main__':
    pt = Prayer_times("../db/information_bot.db")
    message = "prayer times month 10 d 27"
    message = "prayer times 11 29"
    message = "prayer times"
    res = pt.build_response_message(message)
    print(res)