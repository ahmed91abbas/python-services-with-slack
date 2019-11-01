import time
import re
from slackclient import SlackClient
from environs import Env
from services.prayer_times import Prayer_times
from services.todo_list import Todo_list

class App:

    def __init__(self):
        rtm_read_delay = 0.3
        self.mention_regex = "^<@(|[WU].+?)>(.*)"

        self.env = Env()
        self.env.read_env()
        self.slack_client = SlackClient(self.env("SERVICES_BOT_ACCESS_TOKEN"))
        self.starterbot_id = None

        if self.slack_client.rtm_connect(with_team_state=False):
            print("Starter Bot connected and running!")
            self.starterbot_id = self.slack_client.api_call("auth.test")["user_id"]
            while True:
                event = self.parse_events(self.slack_client.rtm_read())
                if event:
                    self.handle_message(event)
                time.sleep(rtm_read_delay)
        else:
            print("Connection failed.")

    def parse_events(self, slack_events):
        for event in slack_events:
            if event["type"] == "message" and not "subtype" in event:
                return event
        return None

    def handle_message(self, event):
        message = event["text"]
        channel = event["channel"]
        user = event["user"]
        if "hi" in message.lower().split(" "):
            response_message = "Hello <@%s>! :tada:" % user
        elif "prayer times" in message.lower():
            response_message = Prayer_times(self.env("DB_FILE")).build_response_message(message)
        elif "todo" in message.lower():
            response_message = Todo_list(self.env("DB_FILE")).build_response_message(message)
        else:
            response_message = 'No service found for your text! Type "Help" to get a list of the available services'

        if type(response_message) is dict:
            r = self.slack_client.api_call(
                "chat.postMessage",
                channel=channel,
                **response_message
            )
        else:
            r = self.slack_client.api_call(
                "chat.postMessage",
                channel=channel,
                text=response_message
            )
        if r["ok"]:
            print("Posted message successfully. ts=" + r["ts"])
        else:
            print("Failed to post message! ts=" + r["ts"])

if __name__ == "__main__":
    App()