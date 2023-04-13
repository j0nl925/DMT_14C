# DMT_14C

This is the repo for DMT Project 14C - Aerodynamic Probe & Data Acquisition

## Table of Contents 
  - Getting Started
    - [Arduino](#Arduino) 
    - VESC
    - Data Acquisition 
    - Hosting The Web App


## Getting Started

### Downloading The Required Libaries
Once you have forked this repo. In your terminal run the following:

```bash
pip install -r requirements.txt
```

This should download all the libraries you need to make the web app functional.

### Arduino
  1. Connect your Arduino board to your computer via USB cable.
  2. Open the Arduino IDE software on your computer.
  3. Copy and paste the code from the [arduino.ino](./arduino/arduino.ino) in this repository into a new sketch in the Arduino IDE.
  4. In the Arduino IDE, select the appropriate board type and port under the Tools menu.
  5. Upload the sketch to the Arduino board by clicking the Upload button in the Arduino IDE.
  6. Open the serial monitor in the Arduino IDE by clicking the magnifying glass icon in the top right corner of the IDE window.
  7. Make sure the baud rate is set to 9600 in the serial monitor.
  8. Open the [actuator.py](./actuator.py) file and run it. 


### VESC
    1. Connect your VESC to the computer via USB
    2. Determine the port that your VESC is connected to by going to the Device Manager on Windows or running the ls /dev/tty* command on Linux or macOS.
    3. Keep note of this port number for when you run your local web app. 
    4. Run the [motor_vesc.py](./motor_vesc.py) file