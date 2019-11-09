import os
import sys
sys.path.append(os.path.abspath('..'))

from services.utils.slack_message_builder import Slack_message_builder
from PyDictionary import PyDictionary
import re


class Dictionary:

    def __init__(self, *args):
        self.action_list = self.init_action_list()
        self.dictionary = PyDictionary()

    def init_action_list(self):
        action_list = {}

        action_list["meaning"] = {}
        action_list["meaning"]["regex"] = '(?:dict|dictionary) meaning of (.*)'
        action_list["meaning"]["function"] = self.get_meaning

        return action_list

    def get_meaning(self, text):
        return self.dictionary.meaning(text)

    def build_response_message(self, text, **kwargs):
        result = self.parse_message(text)

        smb = Slack_message_builder()
        if type(result) is dict:
            for key, value in result.items():
                smb.add_plain_section(f'*{key}*')
                smb.add_formated_section("\n".join(value))
                smb.add_divider()
        elif type(result) is list:
            smb.add_formated_section("\n".join(value))
        else:
            smb.add_plain_section(result)
        return smb.message

    def get_match(self, regex, text):
        p = re.compile(regex, re.IGNORECASE)
        return p.match(text)

    def parse_message(self, text):
        for key, value in self.action_list.items():
            m = self.get_match(value["regex"], text)
            if m:
                return value["function"](m.group(1))
        return "No results found."

if __name__ == '__main__':
    text = "dict meaning of gain"
    dict_service = Dictionary()
    res = dict_service.build_response_message(text=text)
    if type(res) is dict:
        for section in res["blocks"]:
            if section["type"] == "divider":
                print()
            else:
                print(section["text"]["text"])
    else:
        print(res)

