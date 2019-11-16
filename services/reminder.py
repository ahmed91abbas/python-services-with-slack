import time
import re
import datetime
from services.utils.db_manager import Db_manager
from services.utils.slack_message_builder import Slack_message_builder

TABLE_NAME = "reminders"
ID_COL = "generated_id"
TEXT_COL = "text"
CREATED_COL = "created_datetime"
SCHEDULED_COL = "scheduled_datetime"


class Reminder:

    def __init__(self, env, *args):
        self.sec_names = ["s", "sec", "second", "seconds"]
        self.min_names = ["m", "min", "minute", "minutes"]
        self.hour_names = ["h", "hour", "hours"]

        self.db = Db_manager(env("DB_FILE"), TABLE_NAME)

    def create_task(self, text, delta):
        created_datetime = datetime.datetime.now()
        scheduled_datetime = created_datetime + datetime.timedelta(0, delta)
        cols = [TEXT_COL, CREATED_COL, SCHEDULED_COL]
        values = [text, created_datetime, scheduled_datetime]
        return self.db.insert_values(cols, values)

    def delete_task(self, task_id):
        return self.db.delete_where_condition(ID_COL, task_id)

    def delete_all_reminders(self):
        return self.db.delete_all()

    def list_all_reminders(self):
        return self.db.select_all()

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
        cond_re = self.build_cond_re(self.sec_names +
                                     self.min_names +
                                     self.hour_names)
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

    def build_response_message(self, text, **kwargs):
        text, delta = self.parse_message(text)
        if delta:
            task_id = self.create_task(text, delta)
            time.sleep(delta)
            self.delete_task(task_id)
            return "<!channel> Reminder: " + text
        elif type(text) is list:
            if text:
                smb = Slack_message_builder()
                for elem in text:
                    smb.add_formated_section(self.formate_cols(elem))
                return smb.message
            else:
                return "Nothing scheduled."
        else:
            return "Failed to parse reminder message"

    def formate_cols(self, cols):
        text = cols[1]
        scheduled_ts = cols[3]

        scheduled_ts = datetime.datetime.strptime(scheduled_ts,
                                                  '%Y-%m-%d %H:%M:%S.%f')
        scheduled_ts = scheduled_ts.strftime("%Y-%m-%d %H:%M:%S")

        return f"*{text}* - Scheduled at: *{scheduled_ts}*"
