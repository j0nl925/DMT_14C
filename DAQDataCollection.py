# I want to create a script to read voltage channels from a DAQ and plot them in real time

import nidaqmx
import matplotlib.pyplot as plt
import numpy as np
import time
import datetime
import pandas as pd
from matplotlib import animation
import os

def readDAQData(device_name, sampling_rate, samples_per_channel, load_cell_excitation_voltage=5,
                voltage_channels=[], thermocouple_channels=[], load_cell_channels=[]):

    # create the DAQ task
    with nidaqmx.Task() as task:

        # add the voltage channels to the task
        for channel in voltage_channels:
            task.ai_channels.add_ai_voltage_chan("{}/{}".format(device_name, channel),
                                                min_val=-10.0, max_val=10.0)

        # add the thermocouple channels to the task
        for channel in thermocouple_channels:
            task.ai_channels.add_ai_thrmcpl_chan("{}/{}".format(device_name, channel),
                                                 thermocouple_type=nidaqmx.constants.ThermocoupleType.K,
                                                 cjc_source=nidaqmx.constants.CJCSource.CONSTANT_USER_VALUE,
                                                 cjc_val=25.0)

        # add the load cell channels to the task
        for channel in load_cell_channels:
            task.ai_channels.add_ai_voltage_chan("{}/{}".format(device_name, channel),
                                                min_val=-load_cell_excitation_voltage, max_val=load_cell_excitation_voltage)

        # convert sampling_rate and samples_per_channel to appropriate data types
        sampling_rate = np.float64(sampling_rate)
        samples_per_channel = np.uint64(samples_per_channel)

        # configure the timing of the task
        task.timing.cfg_samp_clk_timing(sampling_rate, samps_per_chan=samples_per_channel)

        # read the data from the task
        data = task.read(number_of_samples_per_channel=samples_per_channel)

        # create a dictionary that maps the actual channel names to the column data
        channel_data = {}
        for i, channel in enumerate(voltage_channels):
            channel_data[channel] = data[i]
        for i, channel in enumerate(thermocouple_channels):
            channel_data[channel] = data[i + len(voltage_channels)]
        for i, channel in enumerate(load_cell_channels):
            channel_data[channel] = data[i + len(voltage_channels) + len(thermocouple_channels)]

        return channel_data

def voltage_to_force(data, capacity = 5, rated_output = 1.0):
    A = capacity / rated_output
    force_data = {}
    for channel_name, channel_data in data.items():
        force_data[channel_name] = [A * voltage for voltage in channel_data]
    return force_data

def plotData(axs, data, sampling_rate, window_size, voltage_channels = [], temperature_channels = [], strain_channels = []):
    # Clear the existing plots
    for ax in axs:
        ax.clear()

    
    print(data)
    
    # Set the x-axis values based on the sampling rate
    x_values = data['Seconds']

    # Plot the data for each channel
    for i, channel in enumerate(voltage_channels):
        column_name = 'Voltage Measurement {}'.format(i)
        axs[0].plot(x_values, data[column_name], label='Voltage Channel {}'.format(i))

    for i, channel in enumerate(temperature_channels):
        column_name = 'Temperature Measurement {}'.format(i)
        axs[1].plot(x_values, data[column_name], label='Temperature Channel {}'.format(i))

    for i, channel in enumerate(strain_channels):
        column_name = 'Strain Measurement {}'.format(i)
        axs[2].plot(x_values, data[column_name], label='Strain Channel {}'.format(i))

    # Set the axes limits, labels, and sliding window
    for ax in axs:
        ax.set_xlim(data['Seconds'].iloc[0], data['Seconds'].iloc[-1])
        ax.set_xlabel('Time (s)')
    axs[0].set_ylabel('Voltage (V)')
    axs[1].set_ylabel('Temperature (C)')
    axs[2].set_ylabel('Strain')

    # Add legends to the plots
    axs[0].legend()
    axs[1].legend()
    axs[2].legend()

    # Add gridlines for better visualization
    for ax in axs:
        ax.grid(True)


def findNumberOfChannels(device_name):
    # find the number of channels
    system = nidaqmx.system.System.local()
    for device in system.devices:
        if device.name == device_name:
            number_of_channels = len(device.ai_physical_chans)
            return number_of_channels
        

# write a function to find the device name
def findDeviceName():
    # find the device name
    system = nidaqmx.system.System.local()
    for device in system.devices:
        device_name = device.name
    return device_name

def main():

    global counter
    counter = 0

    # Get the device name and the number of channels
    device_name = findDeviceName()
    num_channels = findNumberOfChannels(device_name)

    # Define the channels and parameters for each type of data
    voltage_channels = ['ai{}'.format(i) for i in range(num_channels)][:4]
    voltage_sampling_rate = 500
    voltage_samples = 100

    temperature_channels = ['ai{}'.format(i) for i in range(num_channels)][4:6]
    temperature_sampling_rate = 5000
    temperature_samples = 100

    strain_channels = ['ai{}'.format(i) for i in range(num_channels)][6:8]
    strain_sampling_rate = 500
    strain_samples = 100

    # Create empty pandas dataframe to store data
    global data_df
    data_df = pd.DataFrame(columns=['Voltage Measurement {}'.format(i) for i in range(len(voltage_channels))] +
                            ['Temperature Measurement {}'.format(i) for i in range(len(temperature_channels))] +
                            ['Strain Measurement {}'.format(i) for i in range(len(strain_channels))])

    fig, axs = plt.subplots(3, 1, figsize=(12, 8))

    # Define the window length (in seconds)
    window_length = 100

    def update_plot(frame):

        global data_df
        global counter

        # Read the data from the DAQ
        voltage_data = readDAQData(device_name=device_name, voltage_channels=voltage_channels,
                                sampling_rate=voltage_sampling_rate,
                                samples_per_channel=voltage_samples)
        
        temperature_data = readDAQData(device_name=device_name, thermocouple_channels=temperature_channels,
                                    sampling_rate=temperature_sampling_rate,
                                    samples_per_channel=temperature_samples)
                
        strain_data = readDAQData(device_name=device_name, voltage_channels=strain_channels,
                                sampling_rate=strain_sampling_rate,
                                samples_per_channel=strain_samples)
        
        strain_data = voltage_to_force(strain_data)

        # Add the data to the DataFrame
        current_time = datetime.datetime.now()
        num_samples = len(voltage_data[voltage_channels[0]])

        seconds = counter * num_samples / voltage_sampling_rate + np.arange(num_samples) / voltage_sampling_rate
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
        data_df = pd.concat([data_df, sample_df], ignore_index=True)

        # Write the data_df to a CSV file, overwriting the existing contents
        csv_file = 'data.csv'
        data_df.to_csv(csv_file, mode='w', index=False)

        counter += 1

        # Update the plot with the latest data
        plotData(axs, data_df[-window_length:], voltage_sampling_rate, window_length, voltage_channels=voltage_channels, temperature_channels=temperature_channels, strain_channels=strain_channels)
        fig.canvas.draw_idle()
        
    ani = animation.FuncAnimation(fig, update_plot, interval=100)
    plt.show()