from flask import Flask, render_template, jsonify

app = Flask(__name__)

led_state=False

@app.route("/", methods=["GET"])
def home():
    return render_template('index.html')

@app.route("/switch_led", methods=["GET"])
def get_led_state():
    global led_state
    led_state = not led_state
    data = {
        "led_state": led_state
    }
    return jsonify(data), 200

if __name__ == "__main__":
    app.run(debug=True)