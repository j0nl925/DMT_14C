from flask import Flask, render_template, request, session, redirect, url_for
from motor_vesc import VESC
from actuator import ArduinoControl
from DAQDataCollection import configureDAQ, readDAQData, main
import threading
import time 
import os


## Stuff to do: 
    # Add checklist in front end for Input Parameters, Connections, Actuator Control, Motor Control, DAQ Data Collection

app = Flask(__name__, static_url_path='/static', template_folder='templates')
app.secret_key = "secret_key"
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

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', input_motor_data=session.get('input_motor_data'))

# Renders softwaremanual page when user clicks on the button
@app.route('/software_manual')
def software_manual():
    return render_template('softwaremanual.html')

# Renders inputparameters page when user clicks on the button
@app.route('/input_parameters')
def input_parameters():
    return render_template('inputparameters.html')

# Renders savedprofiles page when user clicks on the button
@app.route('/saved_profiles')
def saved_profiles():
    return render_template('savedprofiles.html')

# Collects all input parameters
@app.route('/motor_input_parameters', methods=['GET', 'POST'])
def motor_input_parameters():
    input_motor_data = {}

    error_duty_cycle = None
    error_current = None
    error_speed = None
    error_ramp_up_speed = None
    error_ramp_down_speed = None

    error_linear_actuator = None
    error_rotary_motor = None

    if request.method == 'POST':
        duty_cycle = request.form.get('duty_cycle')
        if duty_cycle:
            try:
                duty_cycle = float(duty_cycle)
                if duty_cycle <0 or duty_cycle > 100:
                    error_duty_cycle = {'field': 'duty_cycle', 'message': 'Duty cycle must be between 0 and 100'}
                    duty_cycle = None
                    print(error_duty_cycle)
            except ValueError:
                error_duty_cycle = {'field': 'duty_cycle', 'message': 'Invalid input for duty cycle'}
                duty_cycle = None
                print(error_duty_cycle)
        else:
            error_duty_cycle = {'field': 'duty_cycle', 'message': 'Please enter a value for duty cycle'}
            duty_cycle = None
            print(error_duty_cycle)

        current = request.form.get('current')
        if current:
            try:
                current = float(current)
                if current <0 or current > 5:
                    error_current = {'field': 'current', 'message': 'Current must be between 0 and 5'}
                    current = None
                    print(error_current)
            except ValueError:
                error_current = {'field': 'current', 'message': 'Invalid input for current'}
                current = None
                print(error_current)
        else:
            error_current = {'field': 'current', 'message': 'Please enter a value for current'}
            current = None
            print(error_current)

        speed = request.form.get('speed')
        if speed:
            try:
                speed = float(speed)
                if speed < 0 or speed > 10000:
                    error_speed = {'field': 'speed', 'message': 'Speed must be between 0 and 10,000'}
                    speed = None
                    print(error_speed)
            except ValueError:
                error_speed = {'field': 'speed', 'message': 'Invalid input for speed'}
                print(error_speed)
        else:
            error_speed = {'field': 'speed', 'message': 'Please enter a value for speed'}
            speed = None
            print(error_speed)
        
        ramp_down_speed = request.form.get('ramp_down_speed')
        if ramp_down_speed:
            try:
                ramp_down_speed = float(ramp_down_speed)
                if ramp_down_speed >= speed or ramp_down_speed > 10000:
                    error_ramp_down_speed = {'field': 'ramp_down_speed', 'message': 'Ramp down speed must be between 0 and 10,000 and less than input speed'}
                    ramp_down_speed = None
                    print(error_ramp_down_speed)
            except ValueError:
                error_ramp_down_speed = {'field': 'ramp_down_speed', 'message': 'Invalid input for ramp down speed'}
                print(error_ramp_down_speed)
        else:
            error_ramp_down_speed = {'field': 'ramp_down_speed', 'message': 'Please enter a value for ramp down speed'}
            ramp_down_speed = None
            print(error_ramp_down_speed)
           
        ramp_up_speed = request.form.get('ramp_up_speed')
        if ramp_up_speed:
            try:
                ramp_up_speed = float(ramp_up_speed)
                if ramp_up_speed <= speed or ramp_up_speed > 10000:
                    error_ramp_up_speed = {'field': 'ramp_up_speed', 'message': 'Ramp up speed must be between 0 and 10,000 and greater than input speed'}
                    ramp_up_speed = None
                    print(error_ramp_up_speed)
            except ValueError:
                error_ramp_up_speed = {'field': 'ramp_up_speed', 'message': 'Invalid input for ramp up speed'}
                print(error_ramp_up_speed)
        else:
            error_ramp_up_speed = {'field': 'ramp_up_speed', 'message': 'Please enter a value for ramp up speed'}
            ramp_up_speed = None
            print(error_ramp_up_speed)

        linear_actuator = request.form.get('linear_actuator')
        if linear_actuator:
            try:
                linear_actuator = float(linear_actuator)
                if linear_actuator < 0 or linear_actuator > 100:
                    error_linear_actuator = {'field': 'linear_actuator', 'message': 'Actuator position must be between 0 and 100'}
                    linear_actuator = None
                    print(error_linear_actuator)
            except ValueError:
                error_linear_actuator = {'field': 'linear_actuator', 'message': 'Invalid input for actuator position'}
                print(error_linear_actuator)
        else:
            error_linear_actuator = {'field': 'linear_actuator', 'message': 'Please enter a value for actuator position'}
            linear_actuator = None
            print(error_linear_actuator)
        
        rotary_motor = request.form.get('rotary_motor')
        if rotary_motor:
            try:
                rotary_motor = float(rotary_motor)
                if rotary_motor < 0 or rotary_motor > 360:
                    error_rotary_motor = {'field': 'rotary_motor', 'message': 'Rotary motor position must be between 0 and 360'}
                    rotary_motor = None
                    print(error_rotary_motor)
            except ValueError:
                error_rotary_motor = {'field': 'rotary_motor', 'message': 'Invalid input for rotary position'}
                print(error_rotary_motor)
        else:
            error_rotary_motor = {'field': 'rotary_motor', 'message': 'Please enter a value for rotary position'}
            rotary_motor = None
            print(error_rotary_motor)

        if error_duty_cycle or error_current or error_speed or error_ramp_down_speed or error_ramp_up_speed or error_linear_actuator or error_rotary_motor:
            session['input_motor_data'] = None
            return render_template('inputparameters.html', error_duty_cycle=error_duty_cycle, error_current=error_current, error_speed = error_speed, error_ramp_down_speed=error_ramp_down_speed, error_ramp_up_speed=error_ramp_up_speed, error_linear_actuator=error_linear_actuator, error_rotary_motor=error_rotary_motor, input_motor_data=input_motor_data)

        input_motor_data['duty_cycle'] = duty_cycle
        input_motor_data['current'] = current
        input_motor_data['speed'] = speed
        input_motor_data['ramp_down_speed'] = ramp_down_speed
        input_motor_data['ramp_up_speed'] = ramp_up_speed
        input_motor_data['linear_actuator'] = linear_actuator
        input_motor_data['rotary_motor'] = rotary_motor
        input_motor_data['vesc_port'] = request.form.get('vesc_port')
        session['input_motor_data'] = input_motor_data

        print(input_motor_data)

    input_motor_data = session.get('input_motor_data', {})
    return render_template('inputparameters.html', input_motor_data=input_motor_data)

@app.route('/final_speed_submit', methods=['POST'])
def final_speed_submission():
    final_speed = request.form.get('final_speed')
    print('Final speed = ', final_speed)
    return render_template('index.html')



    #if profile == 'ramp_up':
        #final_speed = int(request.form['final_speed'])
        #motor_control.start(speed, profile, current, duty_cycle, final_speed=final_speed)
    #else:
        #motor_control.start(speed, profile, current, duty_cycle)
        #print('')


@app.route('/motor_profile_selection', methods=['GET', 'POST'])
def motor_profile_selection():
    if request.method == ['POST']:
        motor_profile = request.form.get('motor_profile')
        if motor_profile == 'profile_constant_speed':
            return render_template('index.html')
        if motor_profile == 'profile_ramp_up':
            return render_template('index.html')
        if motor_profile == 'profile_ramp_down':
            return render_template('index.html')
    return render_template('index.html')

# This clears all user inputted data, effectively starting a new session
@app.route('/reset_session', methods=['POST'])
def reset_session():
    session.clear()
    return redirect(url_for('index'))


@app.route('/start_all', methods=['POST'])
def start_all():
    input_motor_data = session.get('input_motor_data', {})
    try:
        vesc = VESC(input_motor_data['vesc_port'])
    except:
        return "Error: VESC port connection not found.", 400

    duty_cycle = input_motor_data['duty_cycle'] / 100
    current = input_motor_data['current']
    speed = input_motor_data['speed']
    profile = 'constant_speed'

    start_motor(vesc, speed, profile, current, duty_cycle)
    start_actuators()
    #start_daq_data_collection()

    return redirect(url_for('index'))

def start_motor(vesc, speed, profile, current, duty_cycle):
    vesc.start_motor(speed, profile, current, duty_cycle)
    temp_thread = threading.Thread(target=check_temp, args=(vesc,))
    temp_thread.start()

def start_actuators():
    # Retrieve linear actuator and rotary motor positions from session
    input_motor_data = session.get('input_motor_data', {})
    linear_position = input_motor_data.get('linear_actuator', 0)
    rotary_position = input_motor_data.get('rotary_motor', 0)

    # Instantiate the ArduinoControl class with the port number
    try:
        arduino = ArduinoControl(input_motor_data['arduino_port'])
    except:
        return "Error: Arduino port connection not found.", 400

    # Move the linear actuator and rotary motor to the specified positions
    try:
        arduino.move_to(linear_position, rotary_position)
    except ValueError as e:
        return str(e), 400

    # Close the serial connection to the Arduino
    arduino.close()

    return "Actuators started successfully!"

def check_temp(vesc):
    while True:
        temperature = vesc.get_temperature()
        if vesc.check_temp(temperature):
            break
        time.sleep(1)

def update_chart():
    # Call the main function from DAQDataCollection.py
    json_p_zero_data, json_p_one_data, json_p_two_data, json_p_three_data, json_strain_gauge_one_data, json_strain_gauge_two_data = main()

    # Render the index.html template and pass the JSON data to the template
    return render_template('index.html',
                           json_p_zero_data=json_p_zero_data,
                           json_p_one_data=json_p_one_data,
                           json_p_two_data=json_p_two_data,
                           json_p_three_data=json_p_three_data,
                           json_strain_gauge_one_data=json_strain_gauge_one_data,
                           json_strain_gauge_two_data=json_strain_gauge_two_data)

@app.route('/stop', methods=['POST'])
def stop():
    # save the data to a csv file
    save_data_to_csv()

    #motor_control.stop()
    return 'OK'



if __name__ == '__main__':
    app.run(debug=True)

