import time
import re
import threading
from slackclient import SlackClient
from environs import Env
from services.prayer_times import Prayer_times
from services.todo_list import Todo_list
from services.reminder import Reminder
from services.services_manual import Services_manual
from services.wikipedia_summary import Wikipedia_summary
from services.dictionary import Dictionary
from services.audio_fetcher import Audio_fetcher


class App:

    def __init__(self):
        self.env = Env()
        self.env.read_env()
        self.bot_id = None
        self.action_list = self.init_action_list()
        # Empty reminder list on start
        Reminder(self.env).delete_all_reminders()

    def init_action_list(self):
        action_list = {}

        action_list["services_manual"] = {}
        action_list["services_manual"]["regex"] = 'help$'
        action_list["services_manual"]["service"] = Services_manual
        action_list["services_manual"]["name"] = 'Services Manual'
        action_list["services_manual"]["discription"] = 'List all'\
            ' the services available and the way to trigger them'

        action_list["todo_list"] = {}
        action_list["todo_list"]["regex"] = '(.*)todo$'
        action_list["todo_list"]["service"] = Todo_list
        action_list["todo_list"]["name"] = 'ToDo List'
        action_list["todo_list"]["discription"] = 'A simple todo list'\
            ' with SQL like commands'

        action_list["reminder"] = {}
        action_list["reminder"]["regex"] = '(?:reminder|remind me)(.*)'
        action_list["reminder"]["service"] = Reminder
        action_list["reminder"]["name"] = 'Reminder Service'
        action_list["reminder"]["discription"] = 'Sends notification at'\
            ' the specified time to the channel'

        action_list["prayer_times"] = {}
        action_list["prayer_times"]["regex"] = 'prayer times(.*)'
        action_list["prayer_times"]["service"] = Prayer_times
        action_list["prayer_times"]["name"] = 'Prayer Times'
        action_list["prayer_times"]["discription"] = 'Get the prayer'\
            ' times for the specified date'

        action_list["wikipedia"] = {}
        action_list["wikipedia"]["regex"] = '(?:wiki|wikipedia) (.*)'
        action_list["wikipedia"]["service"] = Wikipedia_summary
        action_list["wikipedia"]["name"] = 'Wikipedia'
        action_list["wikipedia"]["discription"] = 'Get the summary'\
            ' section from Wikipedia'

        action_list["dictionary"] = {}
        action_list["dictionary"]["regex"] = '(?:dict|dictionary) (.*)'
        action_list["dictionary"]["service"] = Dictionary
        action_list["dictionary"]["name"] = 'Dictionary'
        action_list["dictionary"]["discription"] = 'Get meaning, synonyms,'\
            ' antonyms and examples of a singel English word'

        action_list["audio_fetcher"] = {}
        action_list["audio_fetcher"]["regex"] = 'mp3 http(.*)'
        action_list["audio_fetcher"]["service"] = Audio_fetcher
        action_list["audio_fetcher"]["name"] = 'Audio Fetcher'
        action_list["audio_fetcher"]["discription"] = 'Fetch and upload mp3'\
            ' from the URL. If the URL refers to a video, that video will be'\
            ' converted to mp3'

        return action_list

    def start(self, rtm_read_delay=0.3):
        self.slack_client = SlackClient(self.env("SERVICES_BOT_ACCESS_TOKEN"))
        if self.slack_client.rtm_connect(with_team_state=False):
            print("Starter Bot connected and running!")
            self.bot_id = self.slack_client.api_call("auth.test")["user_id"]
            while True:
                event = self.parse_events(self.slack_client.rtm_read())
                if event:
                    handler_thread = threading.Thread(
                        target=self.handle_message_and_send_response,
                        args=(event,))
                    handler_thread.daemon = True
                    handler_thread.start()

                time.sleep(rtm_read_delay)
        else:
            print("Connection failed.")

    def handle_message_and_send_response(self, event):
        message, channel = self.handle_message(event)
        self.send_response(message, channel)

    def parse_events(self, slack_events):
        for event in slack_events:
            if event["type"] == "message" and "subtype" not in event:
                return event
        return None

    def get_match(self, regex, text):
        p = re.compile(regex, re.IGNORECASE)
        return p.match(text)

    def handle_message(self, event):
        text = event["text"]
        channel = event["channel"]
        response_message = 'No service found for your text!'\
            ' Type "Help" to get a list of the available services'

        for key, value in self.action_list.items():
            if self.get_match(value["regex"], text):
                response_message = value["service"](self.env)\
                  .build_response_message(**event,
                                          action_list=self.action_list)
                return response_message, channel

        return response_message, channel

    def send_response(self, message, channel):
        if type(message) is dict:
            r = self.slack_client.api_call(
                "chat.postMessage",
                channel=channel,
                **message
            )
        else:
            r = self.slack_client.api_call(
                "chat.postMessage",
                channel=channel,
                text=message
            )

        if r["ok"]:
            print("Posted message successfully. ts=" + r["ts"])
        else:
            print(f'Error: {r["error"]}! Date="{r["headers"]["Date"]}')


if __name__ == "__main__":
    App().start()
