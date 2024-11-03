from flask import Flask, render_template, jsonify
import threading
import time
import smtplib
import imaplib
import email
import ssl
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from email.message import EmailMessage

app = Flask(__name__)

# Motor and LED variables
led_state = False
motor_status = False
temp = 25
threshold = 24

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
    return jsonify({"led_state": led_state}), 200

@app.route("/get_led_state", methods=["GET"])
def get_led_state():
    global led_state
    return jsonify({"led_state": led_state}), 200

@app.route("/get_motor_status", methods=["GET"])
def get_motor_status():
    global motor_status
    return jsonify({"motor_status": motor_status}), 200

def send_email():
    port = 465
    smtp_server = "smtp.gmail.com"

    message = EmailMessage()
    message["Subject"] = email_subject
    message["From"] = sender_email
    message["To"] = receiver_email
    message.set_content("""Do you want to turn on the fan? Reply "YES" or "NO". You have 1 minute to respond.""")

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, email_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

@app.route("/start_motor", methods=["GET"])
def start_motor():
    global motor_status
    motor_status = True
    # GPIO control logic to start the motor here
    return jsonify({"status": motor_status}), 200

@app.route("/stop_motor", methods=["GET"])
def stop_motor():
    global motor_status
    motor_status = False
    # GPIO control logic to stop the motor here
    return jsonify({"status": motor_status}), 200

def check_for_reply(sent_time):
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(sender_email, email_password)
        mail.select('inbox')
        status, data = mail.search(None, f'UNSEEN SUBJECT "{email_subject}"')
        email_ids = data[0].split()

        for e_id in email_ids:
            status, msg_data = mail.fetch(e_id, '(RFC822)')
            msg = email.message_from_bytes(msg_data[0][1])
            email_date = parsedate_to_datetime(msg['Date'])
            body = msg.get_payload(decode=True).decode()

            if body.strip().upper() == 'YES' and sent_time <= email_date <= (sent_time + timedelta(minutes=1)):
                return True
        mail.logout()
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def monitor_temp():
    while temp > threshold:
        sent_time = datetime.now()
        send_email()
        time.sleep(60)
        if check_for_reply(sent_time):
            print("Fan turned on!")
        else:
            print("No valid reply received.")

def initiate_temp_thread():
    thread = threading.Thread(target=monitor_temp)
    thread.daemon = True
    thread.start()

if __name__ == "__main__":
    initiate_temp_thread()
    app.run(debug=True, host="0.0.0.0", port=5000)
