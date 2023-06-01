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

        while True:
            if self.ser.in_waiting > 0:
                response = self.ser.readline().strip().decode()

                if response == 'OK':
                    print('Position set successfully')
                    break
                elif 'ERROR' in response:
                    raise ValueError('Error setting position')
                else:
                    continue  # ignore any other responses

    def close(self):
        self.ser.close()

# Create an instance of the ArduinoControl class
arduino = ArduinoControl('COM3') 

try:
    while True:
        try:
            # Prompt the user for input
            linear_pos = int(input('Enter linear position (mm): '))

            # Move the linear actuator to the specified position
            arduino.move_to(linear_pos)

            go_back = int(input('Enter 0 to go back to the original position or any other value to continue: '))
            if go_back == 0:
                arduino.move_to(0)
            else:
                break  # Exit the loop if user inputs a value other than 0

        except ValueError as e:
            print('Error:', str(e))

finally:
    # Close the serial connection
    arduino.close()

