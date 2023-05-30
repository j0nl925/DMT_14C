import nidaqmx
import pandas as pd
import numpy as np
import datetime
import sys
import traceback

strain_task = None
experiment_running = True # Flag to track if the experiment is running

def configureDAQ(device_name, type, channels, sampling_rate, samples_per_channel, buffer_size=10000000):
    task = nidaqmx.Task()

    for channel in channels:
        full_channel_name = "{}/{}".format(device_name, channel)
        if type == 'strain':
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

def initializeDAQTasks(strain_device,
    strain_channels,
    strain_sampling_rate,
    strain_samples):
    global strain_task

    if strain_task is not None:
        strain_task.close()
        strain_task = None

    strain_task = configureDAQ(device_name=strain_device, type='strain', channels=strain_channels,
                            sampling_rate=strain_sampling_rate, samples_per_channel=strain_samples)

    tasks = {
        'strain': strain_task
    }

    return tasks

def readDAQData(task, samples_per_channel, channels, type):
    try:
        data = task.read(number_of_samples_per_channel=samples_per_channel)
        channel_data = {}
        if len(channels) == 1:
                channel_data[channels[0]] = data
            else:
                for i, channel in enumerate(channels):
                    if type == 'strain':
                        channel_data[channel] = data[i]

            return channel_data

    except nidaqmx.errors.DaqReadError as e:
        print("Error while reading DAQ data:", e)
        return None
    
def main():
    global experiment_running

    # Define the channels and parameters for strain data
    strain_device = 'Strain_Device'
    strain_channels = ['ai0', 'ai1']
    strain_sampling_rate = 100
    strain_samples = 100


    # Create empty pandas dataframe to store data
    data_df = pd.DataFrame(columns=['Strain Measurement {}'.format(i) for i in range(len(strain_channels))])

    # Initialize the DAQ tasks
    tasks = initializeDAQTasks(strain_device=strain_device,
                            strain_channels=strain_channels,
                            strain_sampling_rate=strain_sampling_rate,
                            strain_samples=strain_samples)

    strain_task = tasks['strain']


    try:
        while experiment_running:

            # Read the data from the DAQ tasks
            strain_data = readDAQData(strain_task, samples_per_channel=strain_samples, channels=strain_channels,
                                    type='strain')

            if strain_data is not None:
                # Add the data to the DataFrame
                current_time = datetime.datetime.now()
                num_samples = len(strain_data[strain_channels[0]])
                seconds_per_sample = 1.0 / strain_sampling_rate
                seconds = np.arange(num_samples) * seconds_per_sample

                sample = {'Time': [current_time] * num_samples, 'Seconds': seconds}

                for i, channel in enumerate(strain_channels):
                    column_name = 'Strain Measurement {}'.format(i)
                    sample[column_name] = pd.Series(strain_data[channel])

                # Convert the sample dictionary to a DataFrame
                sample_df = pd.DataFrame(sample)

                print(sample_df)

                # Append the sample dataframe to the data dataframe
                data_df = data_df.append(sample_df, ignore_index=True)

    except:
        print("Error while running experiment:", sys.exc_info()[0])
        traceback.print_exc()
        experiment_running = False
