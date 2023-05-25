#include <AccelStepper.h>

// Define the pins for the rotary actuator
const uint8_t ROTARY_STEP_PIN = 4;
const uint8_t ROTARY_DIR_PIN = 3;

// Define the resolution of the rotary actuator
const float ROTARY_RESOLUTION = 1.8;

// Define the stroke of the rotary actuator
const float ROTARY_STROKE = 360.0;

// Define the number of steps per revolution for the rotary actuator
const int ROTARY_STEPS_PER_REVOLUTION = 200;

// Define the number of steps per degree for the rotary actuator
const float ROTARY_STEPS_PER_DEGREE = ROTARY_STEPS_PER_REVOLUTION / ROTARY_STROKE;

// Define the rotary actuator
AccelStepper rotaryActuator(AccelStepper::DRIVER, ROTARY_STEP_PIN, ROTARY_DIR_PIN);

// Define initial position for the rotary actuator
int rotPosition = 0;

void setup() {
  // Set the maximum speed and acceleration for the rotary actuator
  rotaryActuator.setMaxSpeed(1000);
  rotaryActuator.setAcceleration(1000);
  
  // Initialize the serial communication
  Serial.begin(9600);
}

void loop() {
  // set current position as 0
  rotaryActuator.setCurrentPosition(0); 

  // read user input for rotary position
  Serial.println("Enter rotary position (degrees):");
  while (Serial.available() == 0) {
    // Wait for user input
  }
  rotPosition = Serial.parseFloat();

  // move the rotary actuator to the specified position
  rotaryActuator.moveTo(rotPosition * ROTARY_STEPS_PER_DEGREE);
  rotaryActuator.run();
 
}

// move to zero position after the loop
// rotaryActuator.moveTo(0);

