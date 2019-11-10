
class Slack_message_builder:

    def __init__(self):
        self.message = {}
        self.message["blocks"] = []

    def add_divider(self):
        divider = {"type": "divider"}
        self.message["blocks"].append(divider)

    def add_plain_section(self, elements):
        self.add_section("plain_text", elements)

    def add_formated_section(self, elements):
        self.add_section("mrkdwn", elements)

    def add_section(self, section_type, elements):
        if not type(elements) is list:
            elements = [elements]
        for elem in elements:
            section = {}
            section["type"] = "section"
            section["text"] = {}
            section["text"]["type"] = "mrkdwn"
            section["text"]["text"] = elem
            self.message["blocks"].append(section)

    def add_context(self, elements):
        context = {}
        context["type"] = "context"
        context["elements"] = []
            
        if not type(elements) is list:
            elements = [elements]
            
        for elem in elements:
            context_element = {}
            context_element["type"] = "mrkdwn"
            context_element["text"]= elem
            context["elements"].append(context_element)
        self.message["blocks"].append(context)