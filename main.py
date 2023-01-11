import pandas as pd
import matplotlib.pyplot as plt
import pythonNIDAQ

def readDAQData(type, device_name, no_of_channels, sample_rate, num_samples):

    # Create instance of nidaqmxWrappers class
    nidaq = pythonNIDAQ.nidaqmxWrappers()

    # Create task
    task = nidaq.returnTaskObj()

    # Add channels to task
    if type == 'voltage':
        task.ai_channels.add_ai_voltage_chan(device_name + '/ai0:' + str(no_of_channels - 1))
    elif type == 'temperature':
        task.ai_channels.add_ai_thrmstr_chan_vex(device_name + '/ai0:' + str(no_of_channels - 1))
    elif type == 'strain':
        task.ai_channels.add_ai_voltage_chan(device_name + '/ai0:' + str(no_of_channels - 1))

    # Set sample rate
    task.timing.cfg_samp_clk_timing(sample_rate)

    task.start()
    data = task.read(num_samples)
    task.stop()
    task.clear()
    task.close()

    return data


def main(no_of_voltage_channels, voltage_sampling_rate, no_of_voltage_samples, no_of_temperature_channels, temperature_sampling_rate, no_of_temperature_samples, no_of_strain_channels, strain_sampling_rate, no_of_strain_samples):
    
    # Create empty pandas dataframe to store data
    df = pd.DataFrame(columns=['Voltage Measurement 0', 'Voltage Measurement 1',
                                'Voltage Measurement 2', 'Voltage Measurement 3',   
                                'Temperature Measurement 0', 'Temperature Measurement 1',
                                'Strain Measurement 0', 'Strain Measurement 1'])

    # Continuously read data and load into dataframe
    while True:

        # Read data from tasks
        voltage_data = readDAQData('voltage', 'Voltage Measurement', no_of_voltage_channels, voltage_sampling_rate, no_of_voltage_samples)
        temperature_data = readDAQData('temperature', 'Temperature Measurement', no_of_temperature_channels, temperature_sampling_rate, no_of_temperature_samples)
        strain_data = readDAQData('strain', 'Strain Measurement', no_of_strain_channels, strain_sampling_rate, no_of_strain_samples)

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

        # Plot data
        df.plot()
        plt.pause(0.0001)

        # Save data to CSV file
        df.to_csv('data.csv')


if __name__ == '__main__':
    main(4, 1000, 1000, 2, 1000, 1000, 2, 1000, 1000)
    
