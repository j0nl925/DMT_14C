import nidaqmx
import numpy as np
import pandas as pd
import datetime

voltage_task = None
temperature_task = None
strain_task = None
experiment_running = False  # Flag to track if the experiment is running

def configureDAQ(device_name, type, channels, sampling_rate, samples_per_channel, buffer_size=10000000):
    task = nidaqmx.Task()

    for channel in channels:
        full_channel_name = "{}/{}".format(device_name, channel)
        if type == 'voltage':
            try:
                task.ai_channels.add_ai_voltage_chan(full_channel_name, min_val=0, max_val=5)
                print("Added voltage channel:", full_channel_name)
            except nidaqmx.errors.DaqError as e:
                print("Error adding voltage channel:", full_channel_name)
                print("Error message:", str(e))
        elif type == 'temperature':
            try:
                task.ai_channels.add_ai_thrmcpl_chan(full_channel_name,
                                                    thermocouple_type=nidaqmx.constants.ThermocoupleType.K,
                                                    cjc_source=nidaqmx.constants.CJCSource.CONSTANT_USER_VALUE,
                                                    cjc_val=25.0)
                print("Added temperature channel:", full_channel_name)
            except nidaqmx.errors.DaqError as e:
                print("Error adding temperature channel:", full_channel_name)
                print("Error message:", str(e))
        elif type == 'strain':
            try:
                task.ai_channels.add_ai_force_bridge_two_point_lin_chan(full_channel_name,
                                                                        min_val=-1.0, max_val=1.0,
                                                                        units=nidaqmx.constants.ForceUnits.KILOGRAM_FORCE,
                                                                        bridge_config=nidaqmx.constants.BridgeConfiguration.HALF_BRIDGE,
                                                                        voltage_excit_source=nidaqmx.constants.ExcitationSource.INTERNAL,
                                                                        voltage_excit_val=5, nominal_bridge_resistance=350.0,
                                                                        electrical_units=nidaqmx.constants.BridgeElectricalUnits.MILLIVOLTS_PER_VOLT,
                                                                        physical_units=nidaqmx.constants.BridgePhysicalUnits.KILOGRAM_FORCE)
                print("Added strain channel:", full_channel_name)
            except nidaqmx.errors.DaqError as e:
                print("Error adding strain channel:", full_channel_name)
                print("Error message:", str(e))

    task.timing.cfg_samp_clk_timing(sampling_rate, samps_per_chan=samples_per_channel,
                                    sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
    task.in_stream.input_buf_size = buffer_size

    return task

def initializeDAQTasks(voltage_device, temperature_device, strain_device,
                       voltage_channels, temperature_channels, strain_channels,
                       voltage_sampling_rate, voltage_samples,
                       temperature_sampling_rate, temperature_samples,
                       strain_sampling_rate, strain_samples):
    global voltage_task
    global temperature_task
    global strain_task

    if voltage_task is not None:
        voltage_task.close()
        voltage_task = None

    if temperature_task is not None:
        temperature_task.close()
        temperature_task = None

    if strain_task is not None:
        strain_task.close()
        strain_task = None

    voltage_task = configureDAQ(device_name=voltage_device, type='voltage', channels=voltage_channels,
                                sampling_rate=voltage_sampling_rate, samples_per_channel=voltage_samples)
    temperature_task = configureDAQ(device_name=temperature_device, type='temperature', channels=temperature_channels,
                                    sampling_rate=temperature_sampling_rate, samples_per_channel=temperature_samples)
    strain_task = configureDAQ(device_name=strain_device, type='strain', channels=strain_channels,
                               sampling_rate=strain_sampling_rate, samples_per_channel=strain_samples)

    tasks = {
        'voltage': voltage_task,
        'temperature': temperature_task,
        'strain': strain_task
    }

    return tasks


initializeDAQTasks(
    voltage_device='Voltage_DAQ',
    temperature_device='Temp_Device',
    strain_device='Strain_Device',
    voltage_channels=['ai0', 'ai1', 'ai2', 'ai3'],
    temperature_channels=['ai0'],
    strain_channels=['ai0', 'ai1'],
    voltage_sampling_rate=100,
    voltage_samples=100,
    temperature_sampling_rate=100,
    temperature_samples=100,
    strain_sampling_rate=100,
    strain_samples=100
)


# Read the data from the specified task
def readDAQData(task, samples_per_channel, channels, type):
    try:
        data = task.read(number_of_samples_per_channel=samples_per_channel)
        channel_data = {}

        if len(channels) == 1:
            channel_data[channels[0]] = data
        else:
            for i, channel in enumerate(channels):
                if type == 'voltage':
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
        print(sample_df)

        #Emit the sample data through the socketIO connection
        #socketIO.emit('data', sample_df.to_json())

        # Close the tasks
        voltage_task.close()
        temperature_task.close()
        strain_task.close()



if __name__ == '__main__':
    main()