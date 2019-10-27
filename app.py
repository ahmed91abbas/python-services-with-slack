from slackeventsapi import SlackEventAdapter
import slack
import os
import json
from environs import Env

env = Env()
env.read_env()

slack_events_adapter = SlackEventAdapter(
    env("SLACK_SIGNING_SECRET"), "/slack/events")
slack_client = slack.WebClient(env("BOT_ACCESS_TOKEN"))

# Message events
@slack_events_adapter.on("message")
def handle_message(event_data):
    message = event_data["event"]
    if is_valid_message(message):
        message_text = message["text"]
        channel = message["channel"]
        if "hi" in message_text.lower():
            response_message = "Hello <@%s>! :tada:" % message["user"]
            response = slack_client.chat_postMessage(channel=channel, text=response_message)

# Error events
@slack_events_adapter.on("error")
def error_handler(err):
    print("ERROR: " + str(err))

def is_valid_message(message):
    #CPW9ATAF9 = General channel
    return (message.get("subtype") is None) \
        and (message["channel"] != "CPW9ATAF9")

slack_events_adapter.start(port=env("PORT"))