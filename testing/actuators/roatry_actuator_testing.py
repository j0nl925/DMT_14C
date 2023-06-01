import serial
import time

class ArduinoControl:
    def __init__(self, port):
        self.ser = serial.Serial(port=port, baudrate=9600, timeout=1)
        time.sleep(2)  # wait for Arduino to initialize

    def move_to(self, rotary_position):
        # Convert position to a string with leading zeros and a newline character
        rotary_position_str = '{:04d}\n'.format(rotary_position)

        # Send position to Arduino over the serial port
        self.ser.write(rotary_position_str.encode())

        # Wait for response from Arduino
        response = self.ser.readline().strip().decode()

        # Check for errors5
        if response == 'OK':
            print('Position set successfully')
        elif response == 'ERROR':
            raise ValueError('Error setting position')
        else:
            raise ValueError('Invalid response from Arduino')

    def close(self):
        self.ser.close()

# Create an instance of the ArduinoControl class
arduino = ArduinoControl('COM3') 

try:
    # Prompt the user for input
    rotary_pos = int(input('Enter rotary position (degrees): '))

    # Move the rotary actuator to the specified position
    arduino.move_to(rotary_pos)

except ValueError as e:
    print('Error:', str(e))

finally:
    # Close the serial connection
    arduino.close()
