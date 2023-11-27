# Twilio package included in Zinco packages tool. If error or not downloaded,
# uncomment the following comment and run this script to enable. Re-comment after installation.
import os
from twilio.rest import Client
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
# This has been generalized for your own Twilio account
# in all marks enclosed with < > replace entire string with your own account information in str format
# example: to='3077976573'

def send(to= '<your phone number>', from_='<Twilio Assigned Phone number>',
         csv_dir=None, filename=None,
         folder=None, flagged_csv=None,
         error=False, is_image=False, flagged=False):
    c = Client('<ACCOUNT SID>',
               '<AUTH TOKEN>')
    if is_image:
        message = c.messages.create(
            body='There was a problem with {}'.format(filename),
            to=to,
            from_=from_)
    elif error:
        message = c.messages.create(
            body='There was a problem with the script',
            to=to,
            from_=from_)
    elif flagged:
        message = c.messages.create(
            body='the CSV {} found several flagged names. You should take a look'.format(flagged_csv),
            to=to,
            from_=from_)
    else:
        message = c.messages.create(
            body=('Success! All images in {} were processed successfully.'
                 '\nCSVs were saved in {}.'
                 '\n Tally ho!'.format(folder, csv_dir)),
            to=to,
            from_=from_)


def send_to_slack(message=None):
    """
    Sends a message to the Slack channel specified in the .env file Used primarily to alert you if the
    code has finished running or if there was an error.
    This requires a .env file with the following variables:
    SLACK_TOKEN = <your slack token>
    CODE_CHANNEL = <the channel you want to send the message to>
    """
    try:
        load_dotenv()
        token = os.getenv('SLACK_TOKEN')
        channel = os.getenv('CODE_CHANNEL')
        client = WebClient(token=token)

    except Warning:
        print('Slack token not found. Add to .env file to enable slack messaging')
        return

    if token is None or channel is None or client is None:
        print('Tokens not found. Add to .env file to enable slack messaging')
        return

    try:
        response = client.chat_postMessage(
            channel=channel,
            text=message)
        assert response["message"]["text"] == message
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        print(f"Got an error: {e.response['error']}")

