# To create a virtual device in NI MAX, follow these steps:

        # Open NI MAX and navigate to Devices and Interfaces > My System.
        # Right-click in the empty space and select Create New.
        # Choose the device type you want to simulate, e.g., NI-9205.
        # Give the virtual device a name and click Finish.
        # The virtual device will now appear in the list of devices under My System.

# To create virtual channels, follow these steps:

        # Right-click on the virtual device in NI MAX and select Create New.
        # Choose the channel type you want to simulate, e.g., thermocouple or strain gauge.
        # Configure the properties of the virtual channel, such as the minimum and maximum values, the sample rate, etc.
        # Once you have created the virtual device and channels, you can use the same readDAQData function in your script to read the data from the virtual channels just as you would from a physical device.

from DAQDataCollection import readDAQData, main
import matplotlib.pyplot as plt
import nidaqmx

if __name__ == "__main__":
        main()

# also need to add in motor control script here 


