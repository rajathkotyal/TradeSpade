import random
from flask import Flask, request
from pymessenger.bot import Bot
import time
import tradespade as ts
import json
import emoji
from datetime import datetime
import os

app = Flask(__name__)       # Initializing our Flask application
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
bot = Bot(ACCESS_TOKEN)
red_heart = emoji.emojize(":red_heart:")
black_circle = emoji.emojize(":black_circle:")
blue_diamond = emoji.emojize(":small_blue_diamond:")
orange_diamond = emoji.emojize(":small_orange_diamond:")
money_bag = emoji.emojize(":money_with_wings:")
exclamation = emoji.emojize(":heavy_exclamation_mark:")
check = emoji.emojize(":heavy_check_mark:")

now = datetime.now()
datetoday = now.strftime("%d/%m/%Y")

#a = defaultdict(list)
# Importing standard route and two requst types: GET and POST.
# We will receive messages that Facebook sends our bot at this endpoint

#dictss = {"hellos":"whats up", "polo":"acd"}
@app.route('/', methods=['GET', 'POST'])

def receive_message():
    #greetlist = ['hola','hello','hi','Hello','Helo','Hi']

    if request.method == 'GET':
        # Before allowing people to message , a verify token is presented
        # that confirms all requests that your bot receives came from Facebook.
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    # If the request was not GET, it  must be POSTand we can just proceed with sending a message
    # back to user
    else:
            # get whatever message a user sent the bot
        output = request.get_json()
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if message.get('message'):
                    # Facebook Messenger ID for user so we know where to send response back to
                    recipient_id = message['sender']['id']
                    #a[recipient_id].append(1)
                    if message['message'].get('text') == "hi" or message['message'].get('text') == "Hi":
                        response_sent_text = greet()
                        send_message(recipient_id, response_sent_text)
                        break

                    if message['message'].get('text') == "stock" or message['message'].get('text') == "Stock":
                        response_sent_text = analysedata()
                        send_message(recipient_id, response_sent_text)
                        time.sleep(2)
                        response_sent_text = analyse()
                        send_message(recipient_id, response_sent_text)
                        time.sleep(3)
                        response_sent_text = stock()
                        send_message(recipient_id, response_sent_text)
                        break

                    if message['message'].get('text') == "help" or message['message'].get('text') == "Help":
                        response_sent_text = help()
                        send_message(recipient_id, response_sent_text)
                        break

                    if message['message'].get('text') == "about" or message['message'].get('text') == "About":
                        response_sent_text = about()
                        send_message(recipient_id, response_sent_text)
                        break

                    elif message['message'].get('text'):
                        response_sent_text = greet()
                        send_message(recipient_id, response_sent_text)
                        break
                    # if user send us a GIF, photo, video or any other non-text item
                    if message['message'].get('attachments'):
                        response_sent_text = greet()
                        send_message(recipient_id, response_sent_text)
        return "Received"


def verify_fb_token(token_sent):
    # take token sent by Facebook and verify it matches the verify token you sent
    # if they match, allow the request, else return an error
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

"""------------------------------------------------------"""

def greet():
    #rec = receive_message()
    greeting = "Hello There! \n\nPlease send me the Keywords : \n"+orange_diamond+" Stock - To get today\'s Stock Predictions. \n"\
+orange_diamond+"About - To get to know how our software analyses the stock market. \n"+orange_diamond+"Help - If you're facing any issues with the software \n\nThank You!"
    return greeting

def about():
    heart = "U+2764"
    dash = "U+2796"
    tick ="U+2705"
    cross = "U+274C"

    aboutmsg = black_circle+" Trade Spade is an Artificially Intelligent software which perform thousands of stock market analytical operations regarding :\n\n" + blue_diamond + "Market Indicators - MacD,RSI\n"+blue_diamond+"Company Risk \
Analysis\n" + blue_diamond + "Twitter & NewsFeed Analysis\n" + blue_diamond + "Natural Language Processing \n\nOn more than 2700 major stocks every single day. (Indian & US Stock Exchanges Combined)  \n\n"+ black_circle +" Once the analysis is complete, \
a real time list of Company Stocks whose values are most likely to increase or decrease on the particular day are returned for you to invest in."+money_bag+"\n\n"+orange_diamond+" NOTE : \nEven \
though the program has a high accuracy rate, the Stock Market can vary drastically.\n\n\
Please use the software only as a reference. We do NOT promise a 100% Profitable Returns."
    return aboutmsg

#And many more algorithms performing thousands of operations per second. \nThese algorithms
"""black_circle+ "Choosing the right stock to invest in has been a gamble for generations. Relying on humans for making trade decsions for us\
has not always been fruitful. But what if there was a software which would do all the hard work for us, only more effectively & reliably? "+computer+"""
def help():
    emo1 = emoji.emojize(":red_heart:")
    helpmsg = "Please Send your issue at trade-spade.business.site \nfor further assistance. \n\nThank You. "+red_heart
    return helpmsg


def analysedata():
    anmsg = "Getting Stock Data :\n"+blue_diamond+" Stock Exchange : NSE India\n"+blue_diamond+" Date : "+datetoday
    return anmsg

def analyse():
    analytics = "Analysing Stock Data. Please Wait. You will be notified soon."
    return analytics

def stock():

    x = ts.gettickers()
    #time.sleep(2)
    return x

# Uses PyMessenger to send response to the user
def send_message(recipient_id, response):
    # sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"



"""response_sent_text = analysedata()
send_message(recipient_id, response_sent_text)
time.sleep(1)
response_sent_text = analyse()
send_message(recipient_id, response_sent_text)
time.sleep(10)"""

# Add description here about this if statement.
if __name__ == "__main__":
    app.run()
