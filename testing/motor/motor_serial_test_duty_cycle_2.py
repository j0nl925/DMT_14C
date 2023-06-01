import time
import csv
import serial
import pyvesc
from pyvesc import VESC
import pyvesc
from pyvesc.VESC.messages import  Alive, SetDutyCycle, SetRPM, GetValues

serialport = "COM4"  # Replace "COM4" with the actual port of your VESC

with serial.Serial(serialport, 115200, timeout=0.1) as ser:
    try:
        for i in range(4, 10):

            for _ in range(5):

                print(i)
                ser.write(pyvesc.encode(Alive())) # Send heartbeat
                ser.write(pyvesc.encode(SetDutyCycle(i/100)))  # Send command to get values
                ser.write(pyvesc.encode_request(GetValues))


                (response, consumed) = pyvesc.decode(ser.read(100))

                # Decode and process the response
                try:
                    decoded_response = pyvesc.decode(response)

                    # Extract specific fields
                    temp_motor = decoded_response.temp_motor
                    duty_cycle_now = decoded_response.duty_cycle_now
                    rpm = decoded_response.rpm
                    avg_motor_current = decoded_response.avg_motor_current
                    avg_input_current = decoded_response.avg_input_current

                    print("Temp Motor:", temp_motor)
                    print("Duty Cycle Now:", duty_cycle_now)
                    print("RPM:", rpm)
                    print("Avg Motor Current:", avg_motor_current)
                    print("Avg Input Current:", avg_input_current)
                    
                except:
                    print("Error decoding response")

                time.sleep(0.1)

                

        time.sleep(5)
        

    except KeyboardInterrupt:
        ser.write(pyvesc.encode(SetRPM(0)))  # Set duty cycle to 0

