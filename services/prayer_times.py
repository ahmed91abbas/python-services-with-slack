import sqlite3
from sqlite3 import Error

#TODO handle saving time

class Prayer_times:

    def __init__(self, db_file):
        self.conn = self.create_connection(db_file)
        try:
            self.conn = sqlite3.connect(db_file)
        except Error as e:
            print(e)

    def create_connection(self, db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Error as e:
            print(e)

        return conn

    def select_time_by_date(self, month_str, day_str=None):
        cur = self.conn.cursor()
        if day_str:
            cur.execute("SELECT day, fajr, sunrise, dhuhr, asr, maghrib, isha \
                FROM prayer_times WHERE month=? AND day=?", (month_str, day_str,))
        else:
            cur.execute("SELECT day, fajr, sunrise, dhuhr, asr, maghrib, isha \
                FROM prayer_times WHERE month=?", (month_str,))

        rows = cur.fetchall()

        return rows

if __name__ == '__main__':
    res = Prayer_times().select_time_by_date("10")
    for r in res:
        print(r)