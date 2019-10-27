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
        print("TODO")
        return rows

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

        print(month, is_dst)
        if month == "10" and not is_dst:
            rows = self.apply_DST_end(rows)

        response_message = ""
        for r in rows:
            for e in r:
                response_message += e + " - "
            response_message += "\n"

        return response_message


if __name__ == '__main__':
    pt = Prayer_times("../db/information_bot.db")
    message = "prayer times month 10 d 27"
    message = "prayer times 11 29"
    message = "prayer times"
    res = pt.build_response_message(message)
    print(res)