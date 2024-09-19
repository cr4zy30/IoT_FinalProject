from flask import Flask, render_template, jsonify
import RPi.GPIO as GPIO

app = Flask(__name__)

LED=25
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(LED, GPIO.OUT)
GPIO.output(LED, 0)
led_state=False

@app.route("/", methods=["GET"])
def home():
    return render_template('dashboard.html')

@app.route("/switch_led", methods=["GET"])
def get_led_state():
    global led_state
    led_state = not led_state
    GPIO.output(LED, led_state)
    data = {
        "led_state": led_state
    }
    return jsonify(data), 200

if __name__ == "__main__":
    app.run(debug=True)