import serial
import time

class ArduinoControl:
    def __init__(self, port):
        self.ser = serial.Serial(port=port, baudrate=9600, timeout=1)

        if not self.ser.is_open:
            self.ser.open()

        time.sleep(2)  # wait for Arduino to initialize
        
    def move_to(self, position):

        position_str = '{}\n'.format(position)
        self.ser.write(position_str.encode())

        response = self.ser.readline().strip().decode()

        if response == 'Position set successfully':
            print('Position set successfully')
        elif response == 'Returned to original position':
            print('Returned to original position')
        elif response == 'Target position reached':
            print('Target position reached')
        else:
            raise ValueError('Invalid response from Arduino')

    def close(self):
        self.ser.close()

# Create an instance of the ArduinoControl class
arduino = ArduinoControl('COM3')

try:
    # Prompt the user for input
    target_pos = int(input('Enter target rotary position (degrees): '))

    # Move the rotary stepper motor to the specified position
    arduino.move_to(target_pos)

    # Prompt the user to return to the original position
    go_back = int(input('Enter 0 to return to the original position: '))

    if go_back == 0:
        arduino.move_to(0.00001)

except ValueError as e:
    print('Error:', str(e))

finally:
    # Close the serial connection
    arduino.close()
