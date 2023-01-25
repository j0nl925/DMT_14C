import pyvesc
import time

# TO DO: 
    # 1. Add a function to check the temperature and then start the ramp up or ramp down using nidaqmx
    # 2. Define Profiles for ramp up, ramp down, constant speed, stop (do we want to do this in GUI or in the code?)

#turn all of the above into a class called VESC and then call the functions from the GUI
class VESC():
    def __init__(self, port):
        self.vesc = pyvesc.VESC(port)
        self.vesc.set_duty_cycle(0.5)
        self.vesc.set_current(10)
        self.vesc.set_rpm(1000)

    def ramp_up(self, initial = 0, final = 1000):
        for i in range(initial, final, 10):
            self.vesc.set_rpm(i)
            time.sleep(0.1)

    def ramp_down(self, initial = 1000, final = 0):
        for i in range(initial, final, -10):
            self.vesc.set_rpm(i)
            time.sleep(0.1)

    def constant_speed(self, speed):
        self.vesc.set_rpm(speed)
        time.sleep(10)

    def stop(self):
        self.vesc.set_rpm(0)

    def start(self, profile = 'ramp_up'):
        if profile == 'ramp_up':
            self.ramp_up()
        elif profile == 'ramp_down':
            self.ramp_down()
        elif profile == 'constant_speed':
            self.constant_speed(1000)
        elif profile == 'stop':
            self.stop()

    def stop_if_above_max_temp(self, temperature, max_temp = 50):
        # get temperature from DAQ
        while True:
            if temperature > 50:
                self.stop()
            else:
                pass
            time.sleep(1)