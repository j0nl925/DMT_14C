from flask import Flask, render_template, request
from VESC import VESC, MotorControl
import threading
import time 

app = Flask(__name__)
vesc = VESC("/dev/ttyACM0")
motor_control = MotorControl(vesc)

# Define maximum temperature
MAX_TEMP = 50

# Function to continuously check the temperature
def check_temp():
    while True:
        temperature = vesc.get_temperature()
        if temperature > MAX_TEMP:
            motor_control.stop()
        time.sleep(1)

# Start temperature checking thread
temp_thread = threading.Thread(target=check_temp)
temp_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start():
    speed = int(request.form['speed'])
    current = int(request.form['current'])
    duty_cycle = float(request.form['duty_cycle'])
    profile = request.form['profile']

    if profile == 'ramp_up':
        final_speed = int(request.form['final_speed'])
        motor_control.start(speed, profile, current, duty_cycle, final_speed=final_speed)
    else:
        motor_control.start(speed, profile, current, duty_cycle)
    return 'OK'


@app.route('/stop', methods=['POST'])
def stop():
    motor_control.stop()
    return 'OK'

if __name__ == '__main__':
    app.run(debug=True)
