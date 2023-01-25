import pyvesc
import time

# TO DO: 
    # 1. Add a function to check the temperature and then start the ramp up or ramp down using nidaqmx
    # 2. Define Profiles for ramp up, ramp down, constant speed, stop (do we want to do this in GUI or in the code?)
    # 3. Turn all of this into a class


#connect to the VESC - assuming USB Connection
vesc = pyvesc.VESC("/dev/ttyUSB0")

# set duty cycle to 50% - need to ask Group A what we want to do here
vesc.set_duty_cycle(0.5)

# set current to 10A
vesc.set_current(10)

# set rpm to 1000
vesc.set_rpm(1000)

def ramp_up(initial = 0, final = 1000):
    for i in range(initial, final, 10):
        vesc.set_rpm(i)
        time.sleep(0.1)

def ramp_down(initial = 1000, final = 0):
    for i in range(initial, final, -10):
        vesc.set_rpm(i)
        time.sleep(0.1)

def constant_speed(speed):
    vesc.set_rpm(speed)
    time.sleep(10)

def stop():
    vesc.set_rpm(0)

def start(profile = 'ramp_up'):
    if profile == 'ramp_up':
        ramp_up()
    elif profile == 'ramp_down':
        ramp_down()
    elif profile == 'constant_speed':
        constant_speed(1000)
    elif profile == 'stop':
        stop()

def stop_if_above_max_temp(temperature, max_temp = 50):
    # get temperature from DAQ
    while True:
        if temperature > 50:
            stop()
        else:
            pass
        time.sleep(1)