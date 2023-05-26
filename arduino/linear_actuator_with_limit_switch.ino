#include <AccelStepper.h>

// Define the pins for the linear actuator
const uint8_t LINEAR_STEP_PIN = 3;
const uint8_t LINEAR_DIR_PIN = 2;
const uint8_t BOTTOM_LIMIT_SWITCH = 7;
const uint8_t TOP_LIMIT_SWITCH = 8;

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
  // Configure the limit switch pins as inputs with pull-up resistors
  pinMode(BOTTOM_LIMIT_SWITCH, INPUT_PULLUP);
  pinMode(TOP_LIMIT_SWITCH, INPUT_PULLUP);

  // Set the maximum speed and acceleration for the linear actuator
  linearActuator.setMaxSpeed(500);
  linearActuator.setAcceleration(500);
  linearActuator.setSpeed(400);

  // Initialize the serial communication
  Serial.begin(9600);
  linearActuator.moveTo(500);
  while (linearActuator.distanceToGo() != 0){
    linearActuator.run();
  }
  int targetPosition0 = 10000;
  linearActuator.moveTo(targetPosition0);
  while (linearActuator.distanceToGo() != 0) {
      if (digitalRead(TOP_LIMIT_SWITCH) == 1) {
        // Stop the linear actuator when the top limit switch is pressed
        linearActuator.stop();
        linearActuator.setCurrentPosition(0);
        linearActuator.moveTo(200);
        while(linearActuator.distanceToGo() != 0){
          linearActuator.run();
        }
      }
      else if (digitalRead(BOTTOM_LIMIT_SWITCH) == 1) {
      // Stop the linear actuator when the top limit switch is pressed
        linearActuator.stop();
        linearActuator.setCurrentPosition(0);  
        linearActuator.moveTo(-1*targetPosition0); 
      }
      linearActuator.run();
    }
}

void loop() {
  // Check if the bottom limit switch is pressed
  // read user input for linear position
  Serial.println("Enter linear position (mm):");
  while (Serial.available() == 0) {
    // Wait for user input
  }
  linPosition = Serial.parseFloat();

  // move linear actuator to the specified position
  int targetPosition = linPosition * LINEAR_STEPS_PER_MM;
  linearActuator.moveTo(targetPosition);
  while (linearActuator.distanceToGo() != 0) {
    if (digitalRead(BOTTOM_LIMIT_SWITCH) == 1) {
      // Move linear actuator to position 0
      linearActuator.stop();
      linearActuator.setCurrentPosition(0); // Reset the actuator's position to 0
      linearActuator.moveTo(-1*targetPosition);
    }
    else if (digitalRead(TOP_LIMIT_SWITCH) == 1) {
      // Stop the linear actuator when the top limit switch is pressed
      linearActuator.stop();
      linearActuator.setCurrentPosition(0);
      linearActuator.moveTo(200);
      while(linearActuator.distanceToGo() != 0){
        linearActuator.run();
      }
    }
    linearActuator.run();
  }

  // print current position
  Serial.print("Current linear position: ");
  Serial.print(linearActuator.currentPosition() / LINEAR_STEPS_PER_MM);
  Serial.println(" mm");

  // Send confirmation to Python
  Serial.println("OK");

  while (Serial.available() > 0) {
    linPosition = Serial.parseFloat();
  }
}