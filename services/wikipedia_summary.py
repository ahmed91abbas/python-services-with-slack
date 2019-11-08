import os
import sys
sys.path.append(os.path.abspath('..'))

import re
import wikipedia
from services.utils.slack_message_builder import Slack_message_builder


class Wikipedia_summary:

    def __init__(self, *args):
        pass

    def build_response_message(self, text, **kwargs):
        search, text = self.parse_message(text)
        try:
            if search:
                text = wikipedia.search(text, results=10)
            else:
                text = wikipedia.summary(text, sentences=10)
        except Exception as e:
            text = str(e)

        smb = Slack_message_builder()
        smb.add_plain_section(text)

        return smb.message

    def get_match(self, regex, text):
        p = re.compile(regex, re.IGNORECASE)
        return p.match(text)

    def parse_message(self, text):
        regex = '(?:wiki|wikipedia) (?:(search) )?(.*)'
        m = self.get_match(regex, text)
        if not m:
            return None, False

        return m.group(1), m.group(2)

if __name__ == '__main__':
    text = "wiki search wikipedia"
    wiki = Wikipedia_summary()
    res = wiki.build_response_message(text=text)
    if type(res) is dict:
        for section in res["blocks"]:
            print(section["text"]["text"])
    else:
        print(res)

