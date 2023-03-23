# TO DO: 
    # 1. Add a check_temp() function to the VESC class to check the temperature and then start the ramp up or ramp down using the DAQ data
    # 2. Define Profiles for ramp up, ramp down, constant speed, stop (do we want to do this in GUI or in the code?)
    # 3. Connect the GUI to the VESC class - when pressing start and stop buttons, the VESC class should be called to start and stop the motor

#need to call these functions from the GUI in the main code

import pyvesc
import threading
import time

class VESC():
    def __init__(self, port):
        self.vesc = pyvesc.VESC(port)
        self.speed = 0
        self.current = 0
        self.duty_cycle = 0
        self.state = 'stopped'

    def config(self):
        if self.duty_cycle < 0 or self.duty_cycle > 1:
            raise ValueError("Duty cycle must be between 0 and 1")
        if self.current < 0 or self.current > 50:
            raise ValueError("Current must be between 0 and 50")
        if self.speed < 0 or self.speed > 5000:
            raise ValueError("Speed must be between 0 and 5000")
        self.vesc.set_duty_cycle(self.duty_cycle)
        self.vesc.set_current(self.current)
        self.vesc.set_rpm(self.speed)
        # Add more configuration settings here, such as fault limits, maximum and minimum RPM, and maximum current
        
    def ramp_up(self, final_speed):
        for i in range(self.speed, final_speed, 10):
            self.vesc.set_rpm(i)
            time.sleep(0.1)
            self.speed = i

    def ramp_down(self, final_speed):
        for i in range(self.speed, final_speed, -10):
            self.vesc.set_rpm(i)
            time.sleep(0.1)
            self.speed = i

    def constant_speed(self):
        self.vesc.set_rpm(self.speed)
        while self.state == 'running':
            time.sleep(0.1)

    def stop(self):
        self.state = 'stopped'
        self.vesc.set_rpm(0)

    def start(self, speed, profile, current, duty_cycle):
        self.speed = speed
        self.current = current
        self.duty_cycle = duty_cycle
        self.state = 'running'
        self.config()
        if profile == 'ramp_up':
            self.ramp_up(speed)
        elif profile == 'ramp_down':
            self.ramp_down(0)
        elif profile == 'constant_speed':
            self.constant_speed()

    def check_temp(self, temperature):
        max_temp = 50
        if temperature > max_temp:
            self.stop()
            return True
        else:
            return False

class MotorControl(threading.Thread):
    def __init__(self, vesc):
        threading.Thread.__init__(self)
        self.vesc = vesc
        self.speed = 0
        self.current = 0
        self.duty_cycle = 0

    def run(self):
        while True:
            temperature = self.vesc.vesc.get_temperature()
            if self.vesc.check_temp(temperature):
                break
            time.sleep(1)

    def start(self, speed, profile, current, duty_cycle):
        self.speed = speed
        self.current = current
        self.duty_cycle = duty_cycle
        if profile == 'ramp_up':
            self.vesc.start(speed, profile, current, duty_cycle, final_speed=speed)
        elif profile == 'ramp_down':
            self.vesc.start(speed, profile, current, duty_cycle)
        elif profile == 'constant_speed':
            self.vesc.start(speed, profile, current, duty_cycle)
        elif profile == 'stop':
            self.vesc.stop()
        else:
            raise ValueError("Invalid profile")
        self.start()

    def stop(self):
        self.vesc.stop()
        self.join()

