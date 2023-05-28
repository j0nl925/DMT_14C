import nidaqmx
import numpy as np
import pandas as pd
import datetime

# Define global variable for the task
global voltage_task

def configureDAQ(device_name, channel, sampling_rate, samples_per_channel, buffer_size=10000000):
    """
    Configure a DAQ task for a voltage channel and add the specified channel to the task.
    """
    global voltage_task
    voltage_task = nidaqmx.Task()
    task = voltage_task
    
    # Add the channel to the task
    task.ai_channels.add_ai_voltage_chan("{}/{}".format(device_name, channel), min_val=0, max_val=5)
            
    # Configure the timing of the task
    task.timing.cfg_samp_clk_timing(sampling_rate, samps_per_chan=samples_per_channel, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)

    task.in_stream.input_buf_size = buffer_size

def readDAQData(samples_per_channel, channel):
    """
    Read the data from the voltage task and return a dictionary mapping the actual
    channel name to the column data. The data is converted to differential pressure values.
    """
    try:
        # Read the data from the task
        data = voltage_task.read(number_of_samples_per_channel=samples_per_channel)

        # Convert voltage data to differential pressure values
        pressure_data = [(voltage / 5.0) * 100.0 * (80.0 / 12.0) - 6.0 for voltage in data]

        # Create a dictionary that maps the channel name to the column data
        channel_data = {channel: pressure_data}
        
        return channel_data
    
    except nidaqmx.errors.DaqReadError as e:
        print("Error while reading DAQ data:", e)
        return None

def main(device='Voltage_DAQ', channel='ai0'):
    # Define the parameters for voltage data
    sampling_rate = 100
    samples = 100

    # Configure the DAQ for voltage data
    configureDAQ(device_name=device, channel=channel, sampling_rate=sampling_rate, samples_per_channel=samples)

    while True:
        # Read the data from the DAQ
        data = readDAQData(samples_per_channel=samples, channel=channel)
        if data is None:
            return

        # Add the data to the DataFrame
        current_time = datetime.datetime.now()
        num_samples = len(data[channel])
        seconds_per_sample = 1.0 / sampling_rate
        seconds = np.arange(num_samples) * seconds_per_sample

        sample = {'Time': [current_time] * num_samples, 'Seconds': seconds, 'Pressure': data[channel]}
        sample_df = pd.DataFrame(sample)
        print(sample_df.to_json(orient='values'))

        return sample_df.to_json(orient='values')
