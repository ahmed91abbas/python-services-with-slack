from slackeventsapi import SlackEventAdapter
import slack
import os
import json
from environs import Env
from collections import deque
from services.prayer_times import Prayer_times

env = Env()
env.read_env()

slack_events_adapter = SlackEventAdapter(
    env("SLACK_SIGNING_SECRET"), "/slack/events")
slack_client = slack.WebClient(env("BOT_ACCESS_TOKEN"))

# Used to prevent responding to events several times
ts_queue = deque([], maxlen=100)

# Message events
@slack_events_adapter.on("message")
def handle_message(event_data):
    message = event_data["event"]
    if is_valid_message(message):
        ts_queue.appendleft(message["ts"])
        message_text = message["text"]
        channel = message["channel"]
        if "hi" in message_text.lower().split(" "):
            response_message = "Hello <@%s>! :tada:" % message["user"]
        elif "prayer times" in message_text.lower():
            response_message = Prayer_times(env("DB_FILE")).build_response_message(message_text)
        else:
            response_message = 'No service found for your text! Type "Help" \
                to get a list of the available services'
        response = slack_client.chat_postMessage(channel=channel, text=response_message)

# Error events
@slack_events_adapter.on("error")
def error_handler(err):
    print("ERROR: " + str(err))

def is_valid_message(message):
    #CPW9ATAF9 = General channel
    return (message.get("subtype") is None) \
        and (message["channel"] != "CPW9ATAF9") \
        and (not message["ts"] in ts_queue)

slack_events_adapter.start(port=env("PORT"))