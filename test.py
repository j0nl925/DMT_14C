#the below code assumes we have 4 different DAQS: one we use all 8 channels and 3 other we are using 2 channels

# TO-DO: 
#   Create a function that reads from a voltage channel
    

import PyDAQmx as daq
import numpy as np
import matplotlib.pyplot as plt

# Create a figure to plot the data
fig, axs = plt.subplots(4, 1, sharex=True)

# Create a task for each DAQ
task1 = daq.Task()
task2 = daq.Task()
task3 = daq.Task()
task4 = daq.Task()

# Set up the analog input channel(s) for each DAQ
# adjust -10 amd 10 to min and max expected voltage of input channel
task1.AIChannels.create_voltage_channel("Dev1/ai0:7", daq.Val_Cfg_Default, -10, 10, daq.Val_Volts, None)
task2.AIChannels.create_voltage_channel("Dev2/ai0:1", daq.Val_Cfg_Default, -10, 10, daq.Val_Volts, None)
task3.AIChannels.create_voltage_channel("Dev3/ai0:1", daq.Val_Cfg_Default, -10, 10, daq.Val_Volts, None)
task4.AIChannels.create_voltage_channel("Dev4/ai0:1", daq.Val_Cfg_Default, -10, 10, daq.Val_Volts, None)

# Set up the sample rate and number of samples to acquire for each DAQ
sample_rate = 10000
samples_per_channel = 1000
task1.timing.cfg_samp_clk_timing(sample_rate, daq.Val_Rising, daq.Val_ContSamps, samples_per_channel)
task2.timing.cfg_samp_clk_timing(sample_rate, daq.Val_Rising, daq.Val_ContSamps, samples_per_channel)
task3.timing.cfg_samp_clk_timing(sample_rate, daq.Val_Rising, daq.Val_ContSamps, samples_per_channel)
task4.timing.cfg_samp_clk_timing(sample_rate, daq.Val_Rising, daq.Val_ContSamps, samples_per_channel)

# Set up the buffer to hold the data for each DAQ
data1 = np.zeros((samples_per_channel, 8))
data2 = np.zeros((samples_per_channel, 2))
data3 = np.zeros((samples_per_channel, 2))
data4 = np.zeros((samples_per_channel, 2))

# Start the acquisition for all tasks
task1.start()
task2.start()
task3.start()
task4.start()

while True:
    # Read the data for each DAQ
    task1.read(samples_per_channel, data1, samples_per_channel, daq.Val_GroupByScanNumber)
    task2.read(samples_per_channel, data2, samples_per_channel, daq.Val_GroupByScanNumber)
    task3.read(samples_per_channel, data3, samples_per_channel, daq.Val_GroupByScanNumber)
    task4.read(samples_per_channel, data4, samples_per_channel, daq.Val_GroupByScanNumber)


    # Plot the data for each DAQ
    for i in range(8):
        axs[0].plot(data1[:, i])
    for i in range(2):
        axs[1].plot(data2[:, i])
        axs[2].plot(data3[:, i])
        axs[3].plot(data4[:, i])
    plt.show(block=False)
    plt.pause(0.1)   # can adjust this to make plot response faster 
    for ax in axs:
        ax.clear()

# Stop the acquisition for all tasks
task1.stop()
task2.stop()
task3.stop()
task4.stop()

# Clean up
task1.clear()
task2.clear()
task3.clear()
task4.clear()
