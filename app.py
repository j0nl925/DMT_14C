from flask import Flask, render_template, request, session, redirect, url_for
from motor_vesc import VESC
from actuator import ArduinoControl
import threading
import nidaqmx
import time 
import os

### Functions for the data acquisition system ###
def configureDAQ(device_name, type, channels, sampling_rate, samples_per_channel, buffer_size=10000000):
    """
    Configure a DAQ task for a specific type of channel (voltage, temperature, or strain)
    and add the specified channels to the task.
    """
    if type == 'voltage':
        global voltage_task
        voltage_task = nidaqmx.Task()
        task = voltage_task
    elif type == 'temperature':
        global temperature_task
        temperature_task = nidaqmx.Task()
        task = temperature_task
    elif type == 'strain':
        global strain_task
        strain_task = nidaqmx.Task()
        task = strain_task

    # Add the channels to the task
    for channel in channels:
        if type == 'voltage':
            task.ai_channels.add_ai_voltage_chan("{}/{}".format(device_name, channel), min_val=0, max_val=5)
        elif type == 'temperature':
            task.ai_channels.add_ai_thrmcpl_chan("{}/{}".format(device_name, channel),
                                                  thermocouple_type=nidaqmx.constants.ThermocoupleType.K,
                                                  cjc_source=nidaqmx.constants.CJCSource.CONSTANT_USER_VALUE,
                                                  cjc_val=25.0)
        elif type == 'strain':
            task.ai_channels.add_ai_force_bridge_two_point_lin_chan("{}/{}".format(device_name, channel),
                                                                     min_val=-1.0, max_val=1.0,
                                                                     units=nidaqmx.constants.ForceUnits.KILOGRAM_FORCE,
                                                                     bridge_config=nidaqmx.constants.BridgeConfiguration.HALF_BRIDGE,
                                                                     voltage_excit_source=nidaqmx.constants.ExcitationSource.INTERNAL,
                                                                     voltage_excit_val=5, nominal_bridge_resistance=350.0,
                                                                     electrical_units=nidaqmx.constants.BridgeElectricalUnits.MILLIVOLTS_PER_VOLT,
                                                                     physical_units=nidaqmx.constants.BridgePhysicalUnits.KILOGRAM_FORCE)
            
    # Configure the timing of the task
    task.timing.cfg_samp_clk_timing(sampling_rate, samps_per_chan=samples_per_channel, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)

    task.in_stream.input_buf_size = buffer_size

def readDAQData(task, samples_per_channel, channels, type):
    """
    Read the data from the specified task and return a dictionary mapping the actual
    channel names to the column data. If the channel is of type 'voltage', it converts
    the data to differential pressure values.
    """
    try:
        # Read the data from the task
        data = task.read(number_of_samples_per_channel=samples_per_channel)

        # Create a dictionary that maps the actual channel names to the column data
        channel_data = {}

        if len(channels) == 1:
            channel_data[channels[0]] = data
        else:
            for i, channel in enumerate(channels):
                if type == 'voltage':
                    # Convert voltage data to differential pressure values
                    voltage_data = data[i]
                    pressure_data = []
                    for voltage in voltage_data:
                        output_percent = (voltage / 5.0) * 100.0
                        pressure = ((80.0 / 12.0) * (output_percent - 10.0)) - 6.0
                        pressure_data.append(pressure)
                    channel_data[channel] = pressure_data
                else:
                    channel_data[channel] = data[i]

        return channel_data
    
    except nidaqmx.errors.DaqReadError as e:
        print("Error while reading DAQ data:", e)
        return None
    
def main(voltage_device='Voltage_DAQ', temperature_device='Temp_Device', strain_device='Strain_Device',
         voltage_channels=['1', '2', '3', '4'], temperature_channels=['1'], strain_channels=['1', '2']):

    # Define the channels and parameters for each type of data
    voltage_channels = ['ai{}'.format(i) for i in range(len(voltage_channels))]
    voltage_sampling_rate = 100
    voltage_samples = 100

    temperature_channels = ['ai{}'.format(i) for i in range(len(temperature_channels))]
    temperature_sampling_rate = 100
    temperature_samples = 100

    strain_channels = ['ai{}'.format(i) for i in range(len(strain_channels))]
    strain_sampling_rate = 100
    strain_samples = 100

    # Create empty pandas dataframe to store data
    data_df = pd.DataFrame(columns=['Voltage Measurement {}'.format(i) for i in range(len(voltage_channels))] +
                                 ['Temperature Measurement {}'.format(i) for i in range(len(temperature_channels))] +
                                 ['Strain Measurement {}'.format(i) for i in range(len(strain_channels))])

    # Configure the DAQ for each type of data
    configureDAQ(device_name=voltage_device, type='voltage', channels=voltage_channels,
                 sampling_rate=voltage_sampling_rate, samples_per_channel=voltage_samples)
    configureDAQ(device_name=temperature_device, type='temperature', channels=temperature_channels,
                 sampling_rate=temperature_sampling_rate, samples_per_channel=temperature_samples)
    configureDAQ(device_name=strain_device, type='strain', channels=strain_channels,
                 sampling_rate=strain_sampling_rate, samples_per_channel=strain_samples)

    while True:
        # Read the data from the DAQ
        voltage_data = readDAQData(voltage_task, samples_per_channel=voltage_samples, channels=voltage_channels,
                                   type='voltage')

        if voltage_data is None:
            return

        temperature_data = readDAQData(temperature_task, samples_per_channel=temperature_samples,
                                       channels=temperature_channels, type='temperature')

        if temperature_data is None:
            return

        strain_data = readDAQData(strain_task, samples_per_channel=strain_samples, channels=strain_channels,
                                  type='strain')

        if strain_data is None:
            return

        # Add the data to the DataFrame
        current_time = datetime.datetime.now()
        num_samples = len(voltage_data[voltage_channels[0]])
        seconds_per_sample = 1.0 / voltage_sampling_rate
        seconds = np.arange(num_samples) * seconds_per_sample

        sample = {'Time': [current_time] * num_samples, 'Seconds': seconds}

        for i, channel in enumerate(voltage_channels):
            column_name = 'Voltage Measurement {}'.format(i)
            sample[column_name] = pd.Series(voltage_data[channel])

        for i, channel in enumerate(temperature_channels):
            column_name = 'Temperature Measurement {}'.format(i)
            sample[column_name] = pd.Series(temperature_data[channel])

        for i, channel in enumerate(strain_channels):
            column_name = 'Strain Measurement {}'.format(i)
            sample[column_name] = pd.Series(strain_data[channel])

        # Convert the sample dictionary to a DataFrame
        sample_df = pd.DataFrame(sample)

        # Append the sample dataframe to the data dataframe
        data_df = data_df.append(sample_df, ignore_index=True)

        #Emit the sample data through the socketIO connection
        #socketIO.emit('data', sample_df.to_json())

        p_zero_data = sample_df[['Seconds', 'Voltage Measurement 0']]
        p_zero_data = p_zero_data.rename(columns={'Seconds': 'Seconds', 'Voltage Measurement 0': 'P_0'})
        json_p_zero_data = p_zero_data.to_json(orient='values')
        print(json_p_zero_data)

        p_one_data = sample_df[['Seconds', 'Voltage Measurement 1']]
        p_one_data = p_one_data.rename(columns={'Seconds': 'Seconds', 'Voltage Measurement 1': 'P_1'})
        json_p_one_data = p_one_data.to_json(orient='values')

        p_two_data = sample_df[['Seconds', 'Voltage Measurement 2']]
        p_two_data = p_two_data.rename(columns={'Seconds': 'Seconds', 'Voltage Measurement 2': 'P_2'})
        json_p_two_data = p_two_data.to_json(orient='values')

        p_three_data = sample_df[['Seconds', 'Voltage Measurement 3']]
        p_three_data = p_three_data.rename(columns={'Seconds': 'Seconds', 'Voltage Measurement 3': 'P_3'})
        json_p_three_data = p_three_data.to_json(orient='values')

        strain_gauge_one_data = sample_df[['Seconds', 'Strain Measurement 0']]
        strain_gauge_one_data = strain_gauge_one_data.rename(columns={'Seconds': 'Seconds', 'Strain Measurement 0': 'Strain_0'})
        json_strain_gauge_one_data = strain_gauge_one_data.to_json(orient='values')

        strain_gauge_two_data = sample_df[['Seconds', 'Strain Measurement 1']]
        strain_gauge_two_data = strain_gauge_two_data.rename(columns={'Seconds': 'Seconds', 'Strain Measurement 1': 'Strain_1'})
        json_strain_gauge_two_data = strain_gauge_two_data.to_json(orient='values')

        return json_p_zero_data, json_p_one_data, json_p_two_data, json_p_three_data, json_strain_gauge_one_data, json_strain_gauge_two_data


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

@app.route('/export_csv', methods=['POST'])
def export_csv():
    # Your export logic here
    return "CSV Exported"

@app.route('/stop', methods=['POST'])
def stop():
    # save the data to a csv file

    #motor_control.stop()
    return 'OK'



if __name__ == '__main__':
    app.run(debug=True)

