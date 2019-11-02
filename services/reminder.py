import time

class Reminder:

    def __init__(self):
        self.delay = 5

    def build_response_message(self, message, channel=None, user=None):
        time.sleep(self.delay)
        to_channel = user
        return "Reminder to ...", to_channel