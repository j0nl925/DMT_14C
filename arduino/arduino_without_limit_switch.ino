#include <AccelStepper.h>

// Define the pins for the linear actuator
const uint8_t LINEAR_STEP_PIN = 5;
const uint8_t LINEAR_DIR_PIN = 6;

// Define the pins for the rotary actuator
const uint8_t ROTARY_STEP_PIN = 3;
const uint8_t ROTARY_DIR_PIN = 4;
const uint8_t rotaryEncoderA = 2;
const uint8_t rotaryEncoderB = 9;

// Define the resolution of the linear and rotary actuators
const float LINEAR_RESOLUTION = 1.8;
const float ROTARY_RESOLUTION = 1.8;

// Define the stroke of the linear and rotary actuators
const float LINEAR_STROKE = 100.0;
const float ROTARY_STROKE = 360.0;

// Define the number of steps per revolution for the linear and rotary actuators
const int LINEAR_STEPS_PER_REVOLUTION = 200;
const int ROTARY_STEPS_PER_REVOLUTION = 200;

// Define the number of steps per mm for the linear actuator
const float LINEAR_STEPS_PER_MM = LINEAR_STEPS_PER_REVOLUTION / LINEAR_STROKE;

// Define the number of steps per degree for the rotary actuator
const float ROTARY_STEPS_PER_DEGREE = ROTARY_STEPS_PER_REVOLUTION / ROTARY_STROKE;

// Define the linear and rotary actuators
AccelStepper linearActuator(AccelStepper::DRIVER, LINEAR_STEP_PIN, LINEAR_DIR_PIN);
AccelStepper rotaryActuator(AccelStepper::DRIVER, ROTARY_STEP_PIN, ROTARY_DIR_PIN);

// Define the rotary encoder
Encoder rotaryEncoder(rotaryEncoderA, rotaryEncoderB);

// Define initial positions for the linear and rotary actuators
int rotPosition = 0;
int linPosition = 0;

void setup() {
  // Set the maximum speed and acceleration for the linear and rotary actuators
  linearActuator.setMaxSpeed(1000);
  linearActuator.setAcceleration(1000);
  rotaryActuator.setMaxSpeed(1000);
  rotaryActuator.setAcceleration(1000);
  
  // Initialize the serial communication
  Serial.begin(9600);
}

void loop() {
  // read user input for linear position
  Serial.println("Enter linear position (mm):");
  while (Serial.available() == 0) {
    // Wait for user input
  }
  linPosition = Serial.parseFloat();

  // read user input for rotary position
  Serial.println("Enter rotary position (degrees):");
  while (Serial.available() == 0) {
    // Wait for user input
  }
  rotPosition = Serial.parseFloat();

  // move linear and rotary actuators to specified positions
  linearActuator.moveTo(linPosition * LINEAR_STEPS_PER_MM);
  linearActuator.run();
  rotaryActuator.moveTo(rotPosition * ROTARY_STEPS_PER_DEGREE);
  rotaryActuator.run();
}
