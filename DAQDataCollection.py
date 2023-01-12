import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import pythonNIDAQ
import nidaqmx
from tkinter import Label, Button
import tkinter as Tk

# the following script requires manual setup of virtual hardware in NI MAX software 
# to do: create a script which allows you to input hardware code name, and then create the virtual hardware automatically
# to do: create a better plotting function - currently it is very slow and only plots on one axes on one figure
# to do: create a function to smoothen out the data points

def readDAQData(type, device_name, no_of_channels, sample_rate, num_samples, voltage_min, voltage_max):

    # Create instance of nidaqmxWrappers class
    nidaq = pythonNIDAQ.nidaqmxWrappers()

    # Create task
    task = nidaq.returnTaskObj()

    # Add channels to task
    if type == 'voltage':
        task.ai_channels.add_ai_voltage_chan(device_name + '/ai0:' + str(no_of_channels - 1), min_val = voltage_min, max_val = voltage_max)
    elif type == 'temperature':
        task.ai_channels.add_ai_thrmcpl_chan(device_name + '/ai0:' + str(no_of_channels - 1), units=nidaqmx.constants.TemperatureUnits.DEG_C,
                                            thermocouple_type=nidaqmx.constants.ThermocoupleType.K)
    elif type == 'strain':
        task.ai_channels.add_ai_force_bridge_two_point_lin_chan(device_name + '/ai0:' + str(no_of_channels - 1), min_val = 0, max_val = 0.005, physical_units=nidaqmx.constants.BridgePhysicalUnits.KILOGRAM_FORCE, #not sure if these configs are correct
                                                             electrical_units=nidaqmx.constants.BridgeElectricalUnits.MILLIVOLTS_PER_VOLT, bridge_config=nidaqmx.constants.BridgeConfiguration.FULL_BRIDGE)

    # Set sample rate
    task.timing.cfg_samp_clk_timing(sample_rate, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)

    task.start()
    data = task.read(num_samples)
    task.stop()
    task.close()

    return data

def update_plot():
    # read data from file
    df = pd.read_csv('data.csv', index_col=0)

    #plot the data
    plt.plot(df['Voltage Measurement 0'], color='red')
    plt.plot(df['Voltage Measurement 1'], color='blue')
    plt.plot(df['Voltage Measurement 2'], color='green')
    plt.plot(df['Voltage Measurement 3'], color='yellow')
    plt.title('Voltage Measurements')
    plt.xlabel('Time')
    plt.ylabel('Voltage')

    plt.plot(df['Temperature Measurement 0'], color='red')
    plt.plot(df['Temperature Measurement 1'], color='blue')
    plt.title('Temperature Measurements')
    plt.xlabel('Time')
    plt.ylabel('Temperature')

    plt.plot(df['Strain Measurement 0'], color='red')
    plt.plot(df['Strain Measurement 1'], color='blue')
    plt.title('Strain Measurements')
    plt.xlabel('Time')
    plt.ylabel('Strain')

    plt.pause(0.0001)

def plotDAQAnimated():
    fig, axs = plt.subplots(nrows=3, figsize=(10, 6),
                       gridspec_kw={'width_ratios': [1], 'wspace': 0.1, 'hspace': 0.4})

    # create the animation
    ani = FuncAnimation(fig, update_plot, interval=1000)
    plt.show()

def main(no_of_voltage_channels, voltage_sampling_rate, no_of_voltage_samples, min_voltage, max_voltage,
        no_of_temperature_channels, temperature_sampling_rate, no_of_temperature_samples,
         no_of_strain_channels, strain_sampling_rate, no_of_strain_samples):
    
    # Create empty pandas dataframe to store data
    df = pd.DataFrame(columns=['Voltage Measurement 0', 'Voltage Measurement 1',
                                'Voltage Measurement 2', 'Voltage Measurement 3',   
                                'Temperature Measurement 0', 'Temperature Measurement 1',
                                'Strain Measurement 0', 'Strain Measurement 1'])

    # Continuously read data and load into dataframe
    while True:

        # Read data from tasks
        voltage_data = readDAQData('voltage', 'Voltage_Measurement', no_of_voltage_channels, voltage_sampling_rate, no_of_voltage_samples, min_voltage, max_voltage)

        for i in range(0,len(voltage_data)):
            df['Voltage Measurement ' + str(i)] = pd.DataFrame(voltage_data[i])

        temperature_data = readDAQData('temperature', 'Temperature_Measurement', no_of_temperature_channels, temperature_sampling_rate, no_of_temperature_samples, 0, 0)

        for i in range(0, len(temperature_data)):
            df['Temperature Measurement ' + str(i)] = pd.DataFrame(temperature_data[i])

        strain_data = readDAQData('strain', 'Strain_Measurement', no_of_strain_channels, strain_sampling_rate, no_of_strain_samples, 0, 0)

        for i in range(0, len(strain_data)):
            df['Strain Measurement ' + str(i)] = pd.DataFrame(strain_data[i]) 

        update_plot()