from flask import Flask, render_template, jsonify, request, redirect, url_for, session, copy_current_request_context
from flask_session import Session
import threading
import time
import RPi.GPIO as GPIO  # uncomment if on Raspberry Pi
import smtplib
import imaplib
import email
import ssl
import paho.mqtt.client as paho
import sys
import sqlite3
import base64
import requests
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from email.message import EmailMessage

app = Flask(__name__)
app.secret_key = 'womp_womp' 
app.config['SESSION_TYPE'] = 'filesystem' 
Session(app) 

from Freenove_DHT import DHT             

# -- GLOBAL VARIABLES --

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

DHTPin = 16

led_state=False
motor_status=False
light_status=False
light_intensity=0


temp=0 # input comes from dht11
threshold=24

sender_email = "zlatintsvetkov@gmail.com"  
email_password = "uimh xpeq ggwf muwm"

MQTT_BROKER = "192.168.50.194"
# MQTT_BROKER = "192.168.0.124"
MQTT_PORT = 1883
RFID_TOPIC = "rfid/tag"
rfid_tag_detected = None
login_queue = ""
# --- DATABASE FUNCTIONS ---
DATABASE = 'db_files/iot_system.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# -- ROUTES -- 


@app.route("/", methods=["GET"])
def home():
    print("entered home()") # DEBUG
    if "user" not in session:  
        print("user NOT in session so redirecting to login") # DEBUG
        return redirect(url_for("login"))

    user_id = session["user"]["id"]
    conn = get_db_connection()
    user = conn.execute("SELECT id, name, email, light_threshold, temp_threshold, profile_picture FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close
    profile_picture = None
    if user["profile_picture"]:
        profile_picture = base64.b64encode(user["profile_picture"]).decode("utf-8")

    return render_template("dashboard.html", user=user, profile_picture=profile_picture)

@app.route("/update_profile", methods=["GET", "POST"])
def update_profile():
    if "user" not in session:
        return redirect(url_for("login"))

    user_id = session["user"]["id"]
    conn = get_db_connection()

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        profile_picture = request.files["profile_picture"]

        # If a new profile picture is uploaded, encode it
        picture_data = None
        if profile_picture and profile_picture.filename != "":
            picture_data = profile_picture.read()

        # Update the user details in the database
        if picture_data:
            conn.execute(
                "UPDATE users SET name = ?, email = ?, profile_picture = ? WHERE id = ?",
                (name, email, picture_data, user_id),
            )
        else:
            conn.execute(
                "UPDATE users SET name = ?, email = ? WHERE id = ?",
                (name, email, user_id),
            )
        conn.commit()
        conn.close()

        # Update the session data
        session["user"]["name"] = name
        session["user"]["email"] = email

        return redirect(url_for("home"))

    # Retrieve the user's current details
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()

    profile_picture = None
    if user["profile_picture"]:
        profile_picture = base64.b64encode(user["profile_picture"]).decode("utf-8")

    return render_template("update_profile.html", user=user, profile_picture=profile_picture)

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


@app.route("/get_temp_humidity", methods=["GET"])
def get_temp_humidity():
    data = get_sensors_info()
    return jsonify(data), 200

# Motor control endpoint
@app.route("/start_motor", methods=["GET"])
def start_motor():
    run_motor()
    return jsonify({"status": motor_status}), 200

# Function to control the motor
@app.route("/stop_motor", methods=["GET"])
def stop_motor():
    global motor_status
    motor_status=False
    GPIO.output(Motor1, GPIO.LOW)  # Stops the motor
    return jsonify({"status": motor_status}), 200

@app.route("/get_motor_state", methods=["GET"])
def get_motor_state():
    global motor_status
    return jsonify({"motor_status": motor_status}), 200

@app.route("/get_light_data", methods=["GET"])
def get_light_data():
    global light_status, light_intensity
    return jsonify({
        "light_intensity": light_intensity,
        "light_status": light_status,
        "email_sent": light_status 
    })


@app.route("/login", methods=["POST", "GET"])
def login():
    global login_queue, light_threshold, temp_threshold
    if request.method == "GET":
        print("Accessing LOGIN from GET") # DEBUG
        if "user" in session:
            print("user has a session") # DEBUG
            return render_template("dashboard.html", user=session['user'])
        return render_template("login.html")

    #--POST--
    print("accsessing LOGIN from POST") # DEBUUG
    # #if you already have a session and are trying to log in, first log out before starting new session
    # if "user" in session:
    #     print("Trying to login when user is already logged in") # DEBUG
    #     session.pop("user", None) 
    if not login_queue:
        return jsonify({"message":"No RFID tags in the queue"}), 200
    rfid_tag = login_queue
    print(f"Processing RFID Tag from queue: {rfid_tag}") # DEBUG
    
    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE rfid_tag = ?", (rfid_tag,)
    ).fetchone()
    conn.close()
    
    if user:
        print("User trying to login EXISTS in DB") #DEBUG
        session["user"] = {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "light_threshold": user["light_threshold"],
            "temp_threshold": user["temp_threshold"],
        }
            # Log user login
        conn = get_db_connection()
        conn.execute(
           "INSERT INTO activity_logs (user_id, action) VALUES (?, ?)",
            (user["id"], "login")
        )
        conn.commit()
        conn.close()
            
        # Send email
        content = (f"User {user['name']} logged in at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        send_email(sender_email, "User Login", content)
        print("session was created for user ")
        print(session["user"]["name"])
        return jsonify({"welcome_message":"Wecome home bratushka"}), 200

    print("User trying to login DOES NOT EXISTS in DB") #DEBUG
    return jsonify({"error": "RFID not recognized"}), 401

@app.route("/logout", methods=["GET"])
def logout():
    global login_queue
    if "user" not in session:
        print("trying to log out despite there not being a session") # DEBUG
        return redirect(url_for("login"))
    # log when user logs out
    user_id = session["user"]["id"]
    
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO activity_logs (user_id, action) VALUES (?, ?)",
        (user_id, "logout")
    )
    conn.commit()
    conn.close()
    session.pop("user", None) 
    print("user successfully logged out") # DEBUG
    login_queue = ""
    return redirect(url_for("login"))


# -- HELPER FUNCTIONS --

def get_sensors_info():
    dht = DHT(DHTPin)
    global temp

    for i in range(0,15):            
        chk = dht.readDHT11()  
        if (chk == 0):  
            print("DHT11,OK!")
            break
        time.sleep(0.1)
    
    temp = round(dht.getTemperature(), 2)

    return {
        "temperature": temp,
        "humidity": round(dht.getHumidity(), 2)
    }

def send_email(receiver, subject, content):
    port = 465
    smtp_server = "smtp.gmail.com"

    message = EmailMessage()
    message["Subject"] = subject;
    message["From"] = sender_email
    message["To"] = receiver
    message.set_content(content)

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, email_password)
            server.sendmail(sender_email, receiver, message.as_string())
            print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")
        return None

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
            response = body.strip().split()[0].lower()
            print("Response:", response)

            return response == 'yes'
            
            print('---')
        
        mail.logout()
        return False
    except Exception as e:
        print(f'Error: {e}')

def monitor_temp():    
    global temp, threshold, motor_status

    while(True):
        if temp > threshold and not motor_status:
            
            print("Waiting 6 seconds...")
            time.sleep(6) # wait before checking the temperature again...

            if temp <= threshold: 
                break

            sent_time = datetime.now()
            subject = "Temperature is getting high... Should we turn on the fan?"
            content = ("""\

                Do you want to turn on the fan? 
                Reply "YES" or "NO"

                Only the FIRST reply will be considered.
                
                Note: you have 1 minute to answer the message, otherwise your response will be ignored.

                """)
            send_email(session["user"]["email"],subject,content)

            time.sleep(20)

            if check_for_reply(sent_time):
                print("Fan turned on!")
                # LOGIC TOO TURN ON THE MOTOR
                run_motor()
            else:
                print("No valid reply received within the time frame.")
        time.sleep(1)

def run_motor():
    global motor_status
    motor_status=True
    # First direction
    GPIO.output(Motor1, GPIO.HIGH)
    GPIO.output(Motor2, GPIO.LOW)
    GPIO.output(Motor3, GPIO.HIGH)
    # time.sleep(5)

    # # Second direction
    # GPIO.output(Motor1, GPIO.HIGH)
    # GPIO.output(Motor2, GPIO.HIGH)
    # GPIO.output(Motor3, GPIO.LOW)
    # time.sleep(5)

    # # Stop the motor
    # GPIO.output(Motor1, GPIO.LOW)
def check_light():
    global light_status, led_state, light_intensity, login_queue

    def on_message(client, userdata, msg):
        global light_status, led_state, light_intensity, login_queue

        if msg.topic == "photoresistor/light_intensity":
            light_intensity = int(msg.payload.decode())
            print(f"Light Intensity: {light_intensity}%")

        elif msg.topic == "photoresistor/light":
            light_status = msg.payload.decode() == "True"
            print(f"Light Status: {light_status}")
            GPIO.output(LED, GPIO.HIGH if light_status else GPIO.LOW)
            led_state = light_status

            # Send email if the light turns on
            if light_status:
                current_time = datetime.now().strftime("%H:%M")
                receiver = session["user"]["email"]
                subject = "Light Status Notification"
                content = (f"The Light is ON at {current_time}")
                send_email(receiver, subject, content)
        elif msg.topic == RFID_TOPIC:
            print("Subscriber received message MATCHING RFID_TOPIC") # DEBUG
            rfid_tag = msg.payload.decode()
            print(f"RFID Tag Detected: {rfid_tag}")
            if login_queue == "":
                login_queue = rfid_tag
                print(f"RFID tag {rfid_tag} added to queue") 
    client = paho.Client()
    client.on_message = on_message

    if client.connect(MQTT_BROKER, MQTT_PORT, 60) != 0:
        print("Could not connect to MQTT Broker!")
        sys.exit(-1)

    client.subscribe("photoresistor/light_intensity")
    client.subscribe("photoresistor/light")
    client.subscribe(RFID_TOPIC)

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("Disconnecting from broker")
    client.disconnect()

# -- PHASE 4 --

# Log user activity in the database
def log_user_activity(user_id, action):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO activity_logs (user_id, action, timestamp) VALUES (?, ?, ?)",
        (user_id, action, datetime.now())
    )
    conn.commit()
    conn.close()

    
if __name__ == "__main__":
    threading.Thread(target=monitor_temp, daemon=True).start()
    threading.Thread(target=check_light, daemon=True).start()
    app.run(debug=True, use_reloader=False)

