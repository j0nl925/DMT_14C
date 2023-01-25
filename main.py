from DAQDataCollection1 import main
import DAQDataCollection1

no_of_voltage_channels = 4
voltage_sampling_rate = 100
no_of_voltage_sample = 100
min_voltage = 0
max_voltage = 5

no_of_temperature_channels = 2
temperature_sampling_rate =  100
no_of_temperature_samples = 100

no_of_strain_channels = 2
strain_sampling_rate =  100
no_of_strain_samples = 100

if __name__ == '__main__':
    main(no_of_voltage_channels, voltage_sampling_rate, no_of_voltage_sample, min_voltage, max_voltage,
        no_of_temperature_channels, temperature_sampling_rate, no_of_temperature_samples,
         no_of_strain_channels, strain_sampling_rate, no_of_strain_samples)
 