import re
import wikipedia
from utils.slack_message_builder import Slack_message_builder


class Wikipedia_summary:

    def __init__(self, *args):
        pass

    def build_response_message(self, text, **kwargs):
        search, text = self.parse_message(text)
        try:
            if search:
                text = wikipedia.search(text, results=10)
            else:
                page = wikipedia.page(text)
                title = page.title
                url = page.url
                summary = page.summary

                smb = Slack_message_builder()
                smb.add_formated_section(f'<{url}|*{title}*>')
                smb.add_plain_section(summary)
                text = smb.message
        except Exception as e:
            text = str(e)

        return text

    def get_match(self, regex, text):
        p = re.compile(regex, re.IGNORECASE)
        return p.match(text)

    def parse_message(self, text):
        regex = '(?:wiki|wikipedia) (?:(search) )?(.*)'
        m = self.get_match(regex, text)
        if not m:
            return None, False

        return m.group(1), m.group(2)
