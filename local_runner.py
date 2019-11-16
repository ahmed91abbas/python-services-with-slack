import argparse
from environs import Env
import uuid
import random
import string
from datetime import datetime


class Local_runner:

    def __init__(self):
        self.env = Env()
        self.env.read_env()
        services_dict = self.init_services_dict()

        parser = argparse.ArgumentParser(
            description='Used for running individual services')
        parser.add_argument("--message", required=True,
                            type=str, help="Message text")
        parser.add_argument("--service",
                            choices=list(services_dict.keys()),
                            required=True, type=str, help="Service name")
        args = parser.parse_args()
        service = args.service
        message = args.message

        self.event = self.slack_event_mock(message)

        services_dict[service]()

    def init_services_dict(self):
        services = {}
        services["prayer_times"] = self.call_prayer_times
        services["todo_list"] = self.call_todo_list
        services["reminder"] = self.call_reminder
        services["wikipedia_summary"] = self.call_wikipedia_summary
        services["dictionary"] = self.call_dictionary
        services["audio_fetcher"] = self.call_audio_fetcher
        return services

    def call_prayer_times(self):
        from services.prayer_times import Prayer_times
        service = Prayer_times(self.env)
        message = service.build_response_message(**self.event)
        self.print_results(message)

    def call_todo_list(self):
        from services.todo_list import Todo_list
        service = Todo_list(self.env)
        message = service.build_response_message(**self.event)
        self.print_results(message)

    def call_reminder(self):
        from services.reminder import Reminder
        service = Reminder(self.env)
        message = service.build_response_message(**self.event)
        self.print_results(message)

    def call_wikipedia_summary(self):
        from services.wikipedia_summary import Wikipedia_summary
        service = Wikipedia_summary(self.env)
        message = service.build_response_message(**self.event)
        self.print_results(message)

    def call_dictionary(self):
        from services.dictionary import Dictionary
        service = Dictionary(self.env)
        message = service.build_response_message(**self.event)
        self.print_results(message)

    def call_audio_fetcher(self):
        from services.audio_fetcher import Audio_fetcher
        service = Audio_fetcher(self.env)
        message = service.build_response_message(**self.event)
        self.print_results(message)

    def print_results(self, message):
        if type(message) is dict:
            for section in message["blocks"]:
                if section["type"] == "divider":
                    print()
                else:
                    print(section["text"]["text"])
        else:
            print(message)

    def generate_random_alphanumeric(self, length):
        random_alphanumeric = ''.join(random.choice(
            string.ascii_uppercase +
            string.ascii_lowercase +
            string.digits) for _ in range(length))
        return random_alphanumeric

    def slack_event_mock(self, text):
        event = {}
        event["client_msg_id"] = str(uuid.uuid4())
        event["suppress_notification"] = False
        event["type"] = "message"
        event["text"] = text
        event["user"] = self.generate_random_alphanumeric(9)
        event["team"] = self.generate_random_alphanumeric(9)
        event["blocks"] = []

        block = {}
        block["type"] = "rich_text"
        block["block_id"] = self.generate_random_alphanumeric(5)
        block["elements"] = []

        element = {}
        element["type"] = "rich_text_section"
        element["elements"] = []

        inside_element = {}
        inside_element["type"] = "text"
        inside_element["text"] = text

        element["elements"].append(inside_element)
        block["elements"].append(element)
        event["blocks"].append(block)

        event["user_team"] = event["team"]
        event["source_team"] = event["team"]
        event["channel"] = self.generate_random_alphanumeric(9)
        event["event_ts"] = datetime.timestamp(datetime.now())
        event["ts"] = event["event_ts"]

        return event


if __name__ == '__main__':
    Local_runner()
