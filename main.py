from flask import Flask, render_template, jsonify
# import RPi.GPIO as GPIO
import smtplib
import imaplib
import email
import ssl
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

from email.message import EmailMessage

import threading
import time

app = Flask(__name__)

# LED=25
# GPIO.setmode(GPIO.BCM)
# GPIO.setwarnings(False)
# GPIO.setup(LED, GPIO.OUT)
# led_state=GPIO.input(LED) is 1
led_state=False

temp_DHT_11=25 # input comes from dht11
temp_threshold=24

sender_email = "vorden2005@gmail.com"  
receiver_email = sender_email
email_password = "acpk ifjp clju ogbx"
email_subject = "Temperature is getting high... Should we turn on the fan?";

@app.route("/", methods=["GET"])
def home():
    return render_template('dashboard.html')

@app.route("/switch_led", methods=["GET"])
def switch_led_state():
    global led_state
    led_state = not led_state
    # GPIO.output(LED, led_state)
    data = {
        "led_state": led_state
    }
    return jsonify(data), 200

@app.route("/get_led_state", methods=["GET"])
def get_led_state():
    global led_state
    return jsonify({"led_state": led_state}), 200

@app.route("/send_email", methods=["POST"])
def send_email():
    port = 465
    smtp_server = "smtp.gmail.com"

    message = EmailMessage()
    message["Subject"] = email_subject;
    message["From"] = sender_email
    message["To"] = receiver_email

    message.set_content("""\

    Do you want to turn on the fan? 
    Answer "YES" or "NO"
    
    Note: you have 1 minute to answer the message, otherwise your response will be ignored.

    """)

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, email_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            # return jsonify({"status": "success"}), 200
    except Exception as e:
        print("err")
        # return jsonify({"status": "error"}), 500

def check_for_reply(sent_time):
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(sender_email, email_password)
        mail.select('inbox')

        search_criteria = f'UNSEEN SUBJECT "{email_subject}"'
        status, data = mail.search(None, search_criteria)
        email_ids = data[0].split()
        
        for e_id in email_ids:
            status, msg_data = mail.fetch(e_id, '(RFC822)')
            msg = email.message_from_bytes(msg_data[0][1])
            subject = msg['subject']
            from_ = msg['from']
            print(f'Subject: {subject}')
            print(f'From: {from_}')
          
            content_type = msg.get_content_type()
            if content_type == 'text/plain':
                body = msg.get_payload(decode=True).decode()
                email_date = parsedate_to_datetime(msg['Date'])

                print('Body (plain text):')
                print(body)
                if email_body.strip().upper() == 'YES' and sent_time <= email_date <= (sent_time + timedelta(minutes=1)):
                    return True
            
            print('---')
        
        mail.logout()
        return False
    except Exception as e:
        print(f'Error: {e}')

def monitor_temp():
    while temp_DHT_11 > temp_threshold:

        # maybe wait 5 seconds and check temp again to avoid 1 sec temp spikes
        sent_time = datetime.now()
        send_email()

        time.sleep(60)

        if check_for_reply(sent_time):
            print("Fan turned on!")
        else:
            print("No valid reply received within the time frame.")


def initiate_temp_thread():
    thread = threading.Thread(target=monitor_temp)
    thread.daemon = True
    thread.start()

    
if __name__ == "__main__":
    initiate_temp_thread()
    app.run(debug=True)