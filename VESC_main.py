from flask import Flask, render_template, request
from VESC import VESC, MotorControl
from DAQDataCollection import readDAQData
import DAQDataCollection
import threading
import time 
import os


app = Flask(__name__, static_url_path='/static', template_folder='templates')
# vesc = VESC("/dev/ttyACM0")
# motor_control = MotorControl(vesc)

# Define maximum temperature
MAX_TEMP = 50

# Function to continuously check the temperature
# def check_temp():
#     while True:
#         temperature = vesc.get_temperature()
#         if temperature > MAX_TEMP:
#             motor_control.stop()
#         time.sleep(1)

# Start temperature checking thread
# temp_thread = threading.Thread(target=check_temp)
# temp_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/software_manual')
def software_manual():
    return render_template('softwaremanual.html')

@app.route('/input_parameters')
def input_parameters():
    return render_template('inputparameters.html')

@app.route('/duty_cycle_submit', methods=['POST'])
def duty_cycle_submission():
    duty_cycle = request.form.get('duty_cycle')
    print('Duty cycle = ', duty_cycle)
    return render_template('index.html')

@app.route('/current_submit', methods=['POST'])
def current_submission():
    current = request.form.get('current')
    print('Current = ', current)
    return render_template('index.html')

@app.route('/speed_submit', methods=['POST'])
def speed_submission():
    speed = request.form.get('speed')
    print('Input speed = ', speed)
    return render_template('index.html')

@app.route('/final_speed_submit', methods=['POST'])
def final_speed_submission():
    final_speed = request.form.get('final_speed')
    print('Final speed = ', final_speed)
    return render_template('index.html')

@app.route('/profile_submit', methods=['POST'])
def profile_submission():
    profile = request.form.get('profile')
    print('Profile = ', profile)
    return render_template('index.html')


    #if profile == 'ramp_up':
        #final_speed = int(request.form['final_speed'])
        #motor_control.start(speed, profile, current, duty_cycle, final_speed=final_speed)
    #else:
        #motor_control.start(speed, profile, current, duty_cycle)
        #print('')



@app.route('/stop', methods=['POST'])
def stop():
    #motor_control.stop()
    return 'OK'

if __name__ == '__main__':
    app.run(debug=True)
