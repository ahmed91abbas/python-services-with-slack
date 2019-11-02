import time
import re

class Reminder:

    def __init__(self):
        self.sec_names = ["s", "sec", "second", "seconds"]
        self.min_names = ["m", "min", "minute", "minutes"]
        self.hour_names = ["h", "hour", "hours"]

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
        after_regex = f'(?:reminder|remind me) to (.*) after (\\d+) ({cond_re})$'

        text = None
        delta = None
        p = re.compile(after_regex, re.IGNORECASE)
        m = p.match(message)
        if m:
            text = m.group(1)
            number = int(m.group(2))
            unit = m.group(3)
            delta = self.convert_to_sec(number, unit)
        return text, delta

    def build_response_message(self, message, from_channel=None, to_channel=None):
        text, delta = self.parse_message(message)
        if delta:
            time.sleep(delta)
            return "Reminder to " + text, to_channel
        else:
            return "Failed to parse reminder message", from_channel


if __name__ == '__main__':
    message = "reminder to x and y after 2 sec"
    Reminder().build_response_message(message)