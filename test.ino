// I have a linear actuator and rotary actuator that I want to control
// They are both stepper motors and are both connected to motor drivers which allow for microstepping via the MS pins of the driver
// I want to be able to control the linear and rotary position of the actuators independently
// The step pin of the motor driver is connected to the Arduino Uno via a digital pin, the linear actuator is connected to pin 5 and the rotary actuator is connected to pin 3
// The direction pin of the motor driver is connected to the Arduino Uno via a digital pin, the linear actuator is connected to pin 6 and the rotary actuator is connected to pin 4
// For now let's assume the MS pins are not connected to anything

// The resolution of the linear and rotary actuators are 1.8 degrees for both
// The linear actuator has a stroke of 100mm
// The rotary actuator has a stroke of 360 degrees

// I also have a limit switch each for the linear and rotary actuators
// The limit switch for the linear actuator is connected to pin 7

// I want to be able to move the linear and rotary actuators to a specific position
// and then when the limit switch is pressed, I want to be able to move the linear and rotary actuators to its zero position


// TO-DO: Need to write pySerial Script to send commands to Arduino

#include <AccelStepper.h>

// Define the pins for the linear actuator
const uint8_t LINEAR_STEP_PIN = 5;
const uint8_t LINEAR_DIR_PIN = 6;
const uint8_t LINEAR_LIMIT_SWITCH = 7;

// Define the pins for the rotary actuator
const uint8_t ROTARY_STEP_PIN = 3;
const uint8_t ROTARY_DIR_PIN = 4;
const uint8_t ROTARY_LIMIT_SWITCH = 8;
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

// Define the number of steps for the linear and rotary actuators
const int LINEAR_STEPS = LINEAR_STROKE * LINEAR_STEPS_PER_MM;
const int ROTARY_STEPS = ROTARY_STROKE * ROTARY_STEPS_PER_DEGREE;

// Define the linear and rotary actuators
AccelStepper linearActuator(AccelStepper::DRIVER, LINEAR_STEP_PIN, LINEAR_DIR_PIN);
AccelStepper rotaryActuator(AccelStepper::DRIVER, ROTARY_STEP_PIN, ROTARY_DIR_PIN);

// Define the rotary encoder
Encoder rotaryEncoder(rotaryEncoderA, rotaryEncoderB);

// Define initial positions for the linear and rotary actuators
int rotPosition = 0;
int linPosition = 0;

void setup() {
  pinMode(LINEAR_LIMIT_SWITCH, INPUT_PULLUP);
  pinMode(ROTARY_LIMIT_SWITCH, INPUT_PULLUP);
  linearActuator.setMaxSpeed(1000);
  linearActuator.setAcceleration(1000);
  rotaryActuator.setMaxSpeed(1000);
  rotaryActuator.setAcceleration(1000);
  Serial.begin(9600);
}

void loop() {
  // read user input for linear position
  Serial.println("Enter linear position (mm):");
  while (Serial.available() == 0) {
    // wait for user input
  }
  linPosition = Serial.parseFloat();

  // read user input for rotary position
  Serial.println("Enter rotary position (degrees):");
  while (Serial.available() == 0) {
    // wait for user input
  }
  rotPosition = Serial.parseFloat();

  // move linear and rotary actuators to specified positions
  linearActuator.moveTo(linPosition * LINEAR_STEPS_PER_MM);
  linearActuator.run();
  rotaryActuator.moveTo(rotPosition * ROTARY_STEPS_PER_DEGREE);
  rotaryActuator.run();

  // check if limit switches are pressed and move to zero position if necessary
  if (digitalRead(LINEAR_LIMIT_SWITCH) == HIGH) {
    linearActuator.moveTo(0);
    linearActuator.runToPosition();
  }
  if (digitalRead(ROTARY_LIMIT_SWITCH) == HIGH) {
    rotaryActuator.moveTo(0);
    rotaryActuator.runToPosition();
  }
}












