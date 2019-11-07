import os
import sys
sys.path.append(os.path.abspath('..'))

import re
import time
from datetime import datetime
from datetime import date
from services.utils.db_manager import Db_manager
from services.utils.slack_message_builder import Slack_message_builder

class Prayer_times:

    def __init__(self, db_file):
        self.column_names = ["day", "fajr", "sunrise", "dhuhr", "asr", "maghrib", "isha"]
        self.regex = 'prayer times(?: month| m)? (\\d{2})(?: day (\\d{2})| d (\\d{2})| (\\d{2}))?'
        self.error_msg = None
        self.db = Db_manager(db_file, "prayer_times")

    def get_times(self, **kwargs):
        #Remove None values from dict
        cond_kwargs = {k:v for k,v in kwargs.items() if v is not None}
        if cond_kwargs:
            rows = self.db.select_where_condition(cond_kwargs, select_cols=self.column_names)
        else:
            return []

        return rows

    def apply_DST_end(self, month, year, rows):
        res_rows = []
        for row in rows:
            res_row = []
            day = row[0]
            ts = datetime.timestamp(datetime(year, int(month), int(day)))
            is_dst = time.localtime(ts).tm_isdst
            res_row.append(day)
            for i in range(1, len(row)):
                e = row[i]
                if is_dst:
                    res_row.append(e)
                else:
                    res_row.append(\
                        format(int(e[:2])-1, '02')\
                        + e[2:])
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

        rows = self.get_times(month=month, day=day)

        smb = Slack_message_builder()

        if not rows:
            #TODO more generic message
            smb.add_plain_section(f"No results found for M {month}, D {day}")
            return smb.message

        now = datetime.now()
        year = datetime.now().year
        month_str = date(year, int(month), 1).strftime('%B')

        if month == "10":
            rows = self.apply_DST_end(month, year, rows)

        smb.add_plain_section(f"Showing results for {month_str}")
        smb.add_formated_section(self.formate_cols(self.column_names, same_style=True))
        for row in rows:
            smb.add_formated_section(self.formate_cols(row))

        return smb.message

    def formate_cols(self, cols, same_style=False):
        text = ""
        switch = True
        for i in range(len(cols)-1):
            if same_style or switch:
                text += cols[i] + " - "
                switch = False
            else:
                text += "*" + cols[i] + "* - "
                switch = True
        if same_style or switch:
            text += cols[len(cols)-1]
        else:
            text += "*" + cols[len(cols)-1] + "*"

        return text


if __name__ == '__main__':
    pt = Prayer_times("../db/services_db.db")
    message = "prayer times"
    message = "prayer times 11"
    message = "prayer times month 10 d 27"
    res = pt.build_response_message(message)
    for section in res["blocks"]:
        print(section["text"]["text"])