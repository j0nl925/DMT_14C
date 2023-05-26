import nidaqmx
import pandas as pd
import numpy as np
import datetime
import sys
import traceback


voltage_task = None
temperature_task = None
strain_task = None
experiment_running = True  # Flag to track if the experiment is running

def configureDAQ(device_name, type, channels, sampling_rate, samples_per_channel, buffer_size=10000000):
    task = nidaqmx.Task()

    for channel in channels:
        full_channel_name = "{}/{}".format(device_name, channel)
        if type == 'voltage':
            try:
                task.ai_channels.add_ai_voltage_chan(full_channel_name, min_val=0, max_val=5)
            except nidaqmx.errors.DaqError as e:
                print("Error message:", str(e))
        elif type == 'temperature':
            try:
                task.ai_channels.add_ai_thrmcpl_chan(full_channel_name,
                                                    thermocouple_type=nidaqmx.constants.ThermocoupleType.K,
                                                    cjc_source=nidaqmx.constants.CJCSource.CONSTANT_USER_VALUE,
                                                    cjc_val=25.0)
            except nidaqmx.errors.DaqError as e:
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
    
def main():

    global experiment_running

    # Define the channels and parameters for each type of data
    voltage_device = 'Voltage_DAQ'
    temperature_device = 'Temp_Device'
    strain_device = 'Strain_Device'
    voltage_channels = ['ai0', 'ai1', 'ai2', 'ai3']
    temperature_channels = ['ai0']
    strain_channels = ['ai0', 'ai1']
    voltage_sampling_rate = 100
    voltage_samples = 100
    temperature_sampling_rate = 100
    temperature_samples = 100
    strain_sampling_rate = 100
    strain_samples = 100


    # Create empty pandas dataframe to store data
    data_df = pd.DataFrame(columns=['Voltage Measurement {}'.format(i) for i in range(len(voltage_channels))] +
                                 ['Temperature Measurement {}'.format(i) for i in range(len(temperature_channels))] +
                                 ['Strain Measurement {}'.format(i) for i in range(len(strain_channels))])

    # Initialize the DAQ tasks
    tasks = initializeDAQTasks(voltage_device=voltage_device,
                               temperature_device=temperature_device,
                               strain_device=strain_device,
                               voltage_channels=voltage_channels,
                               temperature_channels=temperature_channels,
                               strain_channels=strain_channels,
                               voltage_sampling_rate=voltage_sampling_rate,
                               voltage_samples=voltage_samples,
                               temperature_sampling_rate=temperature_sampling_rate,
                               temperature_samples=temperature_samples,
                               strain_sampling_rate=strain_sampling_rate,
                               strain_samples=strain_samples)

    voltage_task = tasks['voltage']
    temperature_task = tasks['temperature']
    strain_task = tasks['strain']


    try:
        while experiment_running:

            # Read the data from the DAQ tasks
            voltage_data = readDAQData(voltage_task, samples_per_channel=voltage_samples, channels=voltage_channels,
                                       type='voltage')
            temperature_data = readDAQData(temperature_task, samples_per_channel=temperature_samples,
                                           channels=temperature_channels, type='temperature')
            strain_data = readDAQData(strain_task, samples_per_channel=strain_samples, channels=strain_channels,
                                       type='strain')

            if voltage_data is not None and temperature_data is not None and strain_data is not None:
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

                print(sample_df)

                # Append the sample dataframe to the data dataframe
                data_df = data_df.append(sample_df, ignore_index=True)

                # Update the last values dictionary
                p_zero_data = sample_df[['Seconds', 'Voltage Measurement 0']]
                p_zero_data = p_zero_data.rename(columns={'Seconds': 'Seconds', 'Voltage Measurement 0': 'P_0'})

                p_one_data = sample_df[['Seconds', 'Voltage Measurement 1']]
                p_one_data = p_one_data.rename(columns={'Seconds': 'Seconds', 'Voltage Measurement 1': 'P_1'})

                p_two_data = sample_df[['Seconds', 'Voltage Measurement 2']]
                p_two_data = p_two_data.rename(columns={'Seconds': 'Seconds', 'Voltage Measurement 2': 'P_2'})

                p_three_data = sample_df[['Seconds', 'Voltage Measurement 3']]
                p_three_data = p_three_data.rename(columns={'Seconds': 'Seconds', 'Voltage Measurement 3': 'P_3'})
                p_three_data_last_value = p_three_data.iloc[voltage_samples-1, 1]

                strain_gauge_zero_data = sample_df[['Seconds', 'Strain Measurement 0']]
                strain_gauge_zero_data = strain_gauge_zero_data.rename(columns={'Seconds': 'Seconds', 'Strain Measurement 0': 'Strain_0'})

                strain_gauge_one_data = sample_df[['Seconds', 'Strain Measurement 1']]
                strain_gauge_one_data = strain_gauge_one_data.rename(columns={'Seconds': 'Seconds', 'Strain Measurement 1': 'Strain_1'})

    except:
        print("Error while running experiment:", sys.exc_info()[0])
        traceback.print_exc()
        experiment_running = False

# call the main function
if __name__ == '__main__':
    main()
    


                