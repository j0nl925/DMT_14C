import nidaqmx
import pandas as pd
import numpy as np
import datetime
import sys
import matplotlib.pyplot as plt
import traceback

import nidaqmx

def list_devices():
    system = nidaqmx.system.System.local()
    for device in system.devices:
        print(device)
        for channel in device.ai_physical_chans:
            print(" ", channel.name)

# list_devices()


voltage_task = None
experiment_running = True  # Flag to track if the experiment is running

def configureDAQ(device_name, channel, sampling_rate, samples_per_channel, buffer_size=10000000):
    task = nidaqmx.Task()

    full_channel_name = "{}/{}".format(device_name, channel)
    try:
        task.ai_channels.add_ai_voltage_chan(full_channel_name, min_val=0, max_val=5)
    except nidaqmx.errors.DaqError as e:
        print("Error message:", str(e))

    task.timing.cfg_samp_clk_timing(sampling_rate, samps_per_chan=samples_per_channel,
                                    sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
    task.in_stream.input_buf_size = buffer_size

    return task

def readDAQData(task, samples_per_channel, channel):
    try:
        data = task.read(number_of_samples_per_channel=samples_per_channel)
        voltage_data = []
        for voltage in data:
            #output_percent = (voltage / 3.3) * 100.0
            pressure = (((voltage - (0.1 * 3.3)) * 20) / (0.8 * 3.3)) - 10
            voltage_data.append(pressure)
        return {channel: voltage_data}

    except nidaqmx.errors.DaqReadError as e:
        print("Error while reading DAQ data:", e)
        return None

def main():

    global experiment_running

    experiment_running = True

    # Define the channel and parameters
    device = 'cDAQ2Mod1'
    channel = 'ai0'
    sampling_rate = 1000
    samples = 100

    # Create empty pandas dataframe to store data
    data_df = pd.DataFrame(columns=['Pressure Measurement'])

    fig, ax = plt.subplots()

    # Initialize the DAQ task
    task = configureDAQ(device_name=device, channel=channel,
                        sampling_rate=sampling_rate, samples_per_channel=samples)

    try:
        while experiment_running:

            # Read the data from the DAQ task
            data = readDAQData(task, samples_per_channel=samples, channel=channel)

            if data is not None:
                # Add the data to the DataFrame
                current_time = datetime.datetime.now()
                num_samples = len(data[channel])
                seconds_per_sample = 1.0 / sampling_rate
                seconds = np.arange(num_samples) * seconds_per_sample

                sample = {'Time': [current_time] * num_samples, 'Seconds': seconds,
                          'Pressure Measurement': pd.Series(data[channel])}

                # Convert the sample dictionary to a DataFrame
                sample_df = pd.DataFrame(sample)

                sample_df.plot(x='Seconds', y='Pressure Measurement', kind = 'line')

                print(sample_df)

                fig.show()

                # Append the sample dataframe to the data dataframe
                data_df = pd.concat([data_df, sample_df], ignore_index = True)

    except:
        print("Error while running experiment:", sys.exc_info()[0])
        traceback.print_exc()
        experiment_running = False

# call the main function
if __name__ == '__main__':
    main()
