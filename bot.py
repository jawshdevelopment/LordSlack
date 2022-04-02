from crypt import methods
from sqlite3 import Timestamp
from tabnanny import check
import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
import string
import logger
from slack_sdk.errors import SlackApiError

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(
    os.environ['SIGNING_SECRET'], "/slack/events", app)

client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
# client.chat_postMessage(channel="test-bot", text="Booting up!")
BOT_ID = client.api_call("auth.test")['user_id']
print(BOT_ID)

welcome_messages = {}
push_up_total = 0
push_ups_by_month = {}
BAD_WORDS = ['hm', 'no', 'jawsh']

class WelcomeMessage:
    START_TEXT = {
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': (
                'Welcome to the Channel! \n\n'
                '*Get Started, or go F yourself!*'
            )
        }
    }

    DIVIDER = {'type':'divider'}
    
    def __init__(self, channel, user):
        self.channel = channel
        self.user = user
        self.icon_emoji = ':robot_face:'
        self.timestamp = ''
        self.completed = False

    def get_message(self):
        return {
            'ts':self.timestamp,
            'channel':self.channel,
            'username': 'Welcome Robot',
            'icon_emoji': self.icon_emoji,
            'blocks': [
                self.START_TEXT, self.DIVIDER, self._get_reaction_task()
            ]
        }

    def _get_reaction_task(self):
        checkmark = ':white_check_mark:'
        if not self.completed:
            checkmark = ':white_large_square:'

        text = f'{checkmark} *React to this message!*'

        return {'type':'section', 'text': {'type': 'mrkdwn', 'text': text}}

def send_welcome_message(channel, user):
    if channel not in welcome_messages:
        welcome_messages[channel] = {}

    if user in welcome_messages[channel]:
        return

    welcome = WelcomeMessage(channel, user)
    message = welcome.get_message()
    response = client.chat_postMessage(**message)
    welcome.timestamp = response['ts']

    if channel not in welcome_messages:
        welcome_messages[channel] = {}
    welcome_messages[channel][user] = welcome

def check_if_bad_words(message):
    msg = message.lower()
    msg = msg.translate(str.maketrans('', '', string.punctuation))

    return any(word in msg for word in BAD_WORDS)


@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')

    if user_id != None and BOT_ID != user_id:

        if text.lower() == 'start':
            send_welcome_message(f'@{user_id}', user_id)
        elif check_if_bad_words(text):
            ts = event.get('thread_ts')
            if ts == None:
                ts = event.get('ts')
            client.chat_postMessage(
                channel=channel_id, thread_ts=ts, text="That's a no from me, Dawg")





@app.route('/pushup-count', methods=['POST'])
def pushup_count():
    # count_pushups()
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    print(f"{data}, {user_id}, {channel_id}")
    client.chat_postMessage(
        channel=channel_id, text=f"I got you boo")
    return Response(), 200

def conversation_history():
    # Store conversation history
    conversation_history = []
    # ID of the channel you want to send the message to
    channel_id = "C036G1KTVJ4"

    try:
        # Call the conversations.history method using the WebClient
        # conversations.history returns the first 100 messages by default
        # These results are paginated, see: https://api.slack.com/methods/conversations.history$pagination
        result = client.conversations_history(channel=channel_id)

        conversation_history = result["messages"]
        print(conversation_history)

        # Print results
        logger.info("{} messages found in {}".format(len(conversation_history), id))

    except SlackApiError as e:
        logger.error("Error creating conversation: {}".format(e))


if __name__ == "__main__":
    app.run(debug=True, port=5001)