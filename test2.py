import pandas as pd
import matplotlib.pyplot as plt
import pythonNIDAQ

# Create instance of nidaqmxWrappers class
nidaq = pythonNIDAQ.nidaqmxWrappers()

# Create tasks for each DAQ device
voltage_task = nidaq.returnTaskObj()
temperature_task = nidaq.returnTaskObj()
strain_task = nidaq.returnTaskObj()

# Add channels to each task - need to adjust parameters here more
voltage_task.ai_channels.add_ai_voltage_chan('Voltage Measurement/ai0:3')
temperature_task.ai_channels.add_ai_thrmstr_chan_vex('Temperature Measurement/ai0:1')
strain_task.ai_channels.add_ai_voltage_chan('Strain Measurement/ai0:1')

# Set sample rate for each channel
voltage_task.timing.cfg_samp_clk_timing(10000)
temperature_task.timing.cfg_samp_clk_timing(10000)
strain_task.timing.cfg_samp_clk_timing(10000)

# Start tasks
voltage_task.start()
temperature_task.start()
strain_task.start()

# Create empty pandas dataframe to store data
df = pd.DataFrame(columns=['Voltage Measurement 0', 'Voltage Measurement 1',
                           'Voltage Measurement 2', 'Voltage Measurement 3',
                           'Temperature Measurement 0', 'Temperature Measurement 1',
                           'Strain Measurement 0', 'Strain Measurement 1'])

# Continuously read data and load into dataframe
while True:
    # Read data from tasks
    voltage_data = voltage_task.read()
    temperature_data = temperature_task.read()
    strain_data = strain_task.read()

    # Store data in dataframe
    df = df.append({'Voltage Measurement 0': voltage_data[0],
                    'Voltage Measurement 1': voltage_data[1],
                    'Voltage Measurement 2': voltage_data[2],
                    'Voltage Measurement 3': voltage_data[3],
                    'Temperature Measurement 0': temperature_data[0],
                    'Temperature Measurement 1': temperature_data[1],
                    'Strain Measurement 0': strain_data[0],
                    'Strain Measurement 1': strain_data[1]
    })

    #create a subplot for voltage, temperature and strain and plot

