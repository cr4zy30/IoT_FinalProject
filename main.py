from flask import Flask, render_template, jsonify
import threading
import time
import RPi.GPIO as GPIO  # uncomment if on Raspberry Pi
import smtplib
import imaplib
import email
import ssl
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from email.message import EmailMessage

app = Flask(__name__)

# Motor and LED Pin setup (if using on Raspberry Pi)
Motor1 = 22  # Enable Pin for motor
Motor2 = 27  # Input Pin
Motor3 = 17  # Input Pin

LED=25
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(LED, GPIO.OUT)
led_state=GPIO.input(LED) is 1
# Initialize GPIO setup for motor
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(Motor1, GPIO.OUT)
GPIO.setup(Motor2, GPIO.OUT)
GPIO.setup(Motor3, GPIO.OUT)

led_state=False
motor_status=False

temp=25 # input comes from dht11
threshold=24

sender_email = ""  
receiver_email = sender_email
email_password = ""
email_subject = "Temperature is getting high... Should we turn on the fan?"

@app.route("/", methods=["GET"])
def home():
    return render_template('dashboard.html')

@app.route("/switch_led", methods=["GET"])
def switch_led_state():
    global led_state
    led_state = not led_state
    GPIO.output(LED, led_state)
    data = {
        "led_state": led_state
    }
    return jsonify(data), 200

@app.route("/get_led_state", methods=["GET"])
def get_led_state():
    global led_state
    return jsonify({"led_state": led_state}), 200

def send_email():
    port = 465
    smtp_server = "smtp.gmail.com"

    message = EmailMessage()
    message["Subject"] = email_subject;
    message["From"] = sender_email
    message["To"] = receiver_email

    message.set_content("""\

    Do you want to turn on the fan? 
    Reply "YES" or "NO"

    Only the FIRST reply will be considered.
    
    Note: you have 1 minute to answer the message, otherwise your response will be ignored.

    """)

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, email_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")
        return None

# Motor control endpoint
@app.route("/start_motor", methods=["GET"])
def start_motor():
    run_motor()
    return jsonify({"status": motor_status}), 200

def check_for_reply(sent_time):
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(sender_email, email_password)
        mail.select('inbox')

        search_criteria = f'UNSEEN SUBJECT "Re: {email_subject}"'
        status, data = mail.search(None, search_criteria)
        email_ids = data[0].split()
        
        now = datetime.now()
        first_reply = {}

        for e_id in email_ids:
            status, msg_data = mail.fetch(e_id, '(RFC822)')
            msg = email.message_from_bytes(msg_data[0][1])
            subject = msg['subject']
            from_ = msg['from']
            print(f'Subject: {subject}')
            print(f'From: {from_}')          

            email_date = parsedate_to_datetime(msg['Date'])

            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode(part.get_content_charset(), errors='replace').strip()
                        break
            else:
                body = msg.get_payload(decode=True).decode()

            print("DATE:", email_date)
            response = body.strip().split()[0].lower();
            print("Response:", response)

            return response == 'yes'
            
            print('---')
        
        mail.logout()
        return False
    except Exception as e:
        print(f'Error: {e}')

def monitor_temp():
    while temp > threshold and not motor_status:
        time.sleep(5) # wait before checking the temperature again...

        if temp <= threshold: 
            break

        sent_time = datetime.now()
        send_email()

        time.sleep(60)

        if check_for_reply(sent_time):
            print("Fan turned on!")
        else:
            print("No valid reply received within the time frame.")

# Function to control the motor
@app.route("/stop_motor", methods=["GET"])
def stop_motor():
    motor_status=False
    GPIO.output(Motor1, GPIO.LOW)  # Stops the motor
    return jsonify({"status": motor_status}), 200

def run_motor():
    motor_status=True
    # First direction
    GPIO.output(Motor1, GPIO.HIGH)
    GPIO.output(Motor2, GPIO.LOW)
    GPIO.output(Motor3, GPIO.HIGH)
    time.sleep(5)

    # Second direction
    GPIO.output(Motor1, GPIO.HIGH)
    GPIO.output(Motor2, GPIO.HIGH)
    GPIO.output(Motor3, GPIO.LOW)
    time.sleep(5)

    # Stop the motor
    GPIO.output(Motor1, GPIO.LOW)
    
@app.route("/get_motor_state", methods=["GET"])
def get_motor_state():
    global motor_status
    return jsonify({"motor_status": motor_status}), 200




def initiate_temp_thread():
    thread = threading.Thread(target=monitor_temp)
    thread.daemon = True
    thread.start()
    
if __name__ == "__main__":
    initiate_temp_thread()
    app.run(debug=True, use_reloader=False)