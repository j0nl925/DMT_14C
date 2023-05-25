#include <AccelStepper.h>

// Define the pins for the linear actuator
const uint8_t LINEAR_STEP_PIN = 3;
const uint8_t LINEAR_DIR_PIN = 2;

// Define the resolution of the linear actuator
const float LINEAR_RESOLUTION = 1.8;

// Define the stroke of the linear actuator
const float LINEAR_STROKE = 100.0;

// Define the number of steps per revolution for the linear actuator
const int LINEAR_STEPS_PER_REVOLUTION = 200;

// Define the number of steps per mm for the linear actuator
const float LINEAR_STEPS_PER_MM = LINEAR_STEPS_PER_REVOLUTION / LINEAR_STROKE;

// Define the linear actuator
AccelStepper linearActuator(AccelStepper::DRIVER, LINEAR_STEP_PIN, LINEAR_DIR_PIN);

// Define initial position for the linear actuator
int linPosition = 0;

void setup() {
  // Set the maximum speed and acceleration for the linear actuator
  linearActuator.setMaxSpeed(1000);
  linearActuator.setAcceleration(1000);

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

  // move linear actuator to the specified position
  linearActuator.moveTo(linPosition * LINEAR_STEPS_PER_MM);
  linearActuator.runToPosition();

  // print current position
  Serial.print("Current linear position: ");
  Serial.print(linearActuator.currentPosition() / LINEAR_STEPS_PER_MM);
  Serial.println(" mm");

  // Send confirmation to Python
  Serial.println("OK");

  while(Serial.available()>0){
    linPosition = Serial.parseFloat();
  }
}
