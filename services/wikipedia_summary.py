import os
import sys
import wikipedia
sys.path.append(os.path.abspath('..'))

import re
from services.utils.slack_message_builder import Slack_message_builder


class Wikipedia_summary:

    def __init__(self, *args):
        pass

    def build_response_message(self, text, **kwargs):
        text = self.parse_message(text)

        text = wikipedia.summary(text)

        smb = Slack_message_builder()
        smb.add_plain_section(text)

        return smb.message

    def get_match(self, regex, text):
        p = re.compile(regex, re.IGNORECASE)
        return p.match(text)

    def parse_message(self, text):
        regex = '(?:wiki|wikipedia) (.*)'
        m = self.get_match(regex, text)
        if m:
            return m.group(1)
        return None

if __name__ == '__main__':
    text = "wiki python"
    wiki = Wikipedia_summary()
    res = wiki.build_response_message(text=text)
    if type(res) is dict:
        for section in res["blocks"]:
            print(section["text"]["text"])
    else:
        print(res)

