from DAQDataCollection import main
import DAQDataCollection

no_of_voltage_channels = 4
voltage_sampling_rate = 5000
no_of_voltage_sample = 500
min_voltage = 0
max_voltage = 5

no_of_temperature_channels = 2
temperature_sampling_rate =  95
no_of_temperature_samples = 75

no_of_strain_channels = 2
strain_sampling_rate =  500
no_of_strain_samples = 50

if __name__ == '__main__':
    main(no_of_voltage_channels, voltage_sampling_rate, no_of_voltage_sample, min_voltage, max_voltage,
        no_of_temperature_channels, temperature_sampling_rate, no_of_temperature_samples,
         no_of_strain_channels, strain_sampling_rate, no_of_strain_samples)
