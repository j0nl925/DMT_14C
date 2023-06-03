#include <AccelStepper.h>

// Define the pins for the rotary stepper motor
const uint8_t ROTARY_STEP_PIN = 4;
const uint8_t ROTARY_DIR_PIN = 5;

// Define the number of steps per revolution for the rotary stepper motor
const int ROTARY_STEPS_PER_REVOLUTION = 200;

// Define the number of steps per degree for the rotary stepper motor
const float ROTARY_STEPS_PER_DEGREE = ROTARY_STEPS_PER_REVOLUTION / 360.0;

// Define the rotary stepper motor
AccelStepper rotaryStepper(AccelStepper::DRIVER, ROTARY_STEP_PIN, ROTARY_DIR_PIN);

// Define zero position for the rotary stepper motor
int zeroPosition = 0;

// Variable to store the target position
int targetRotaryPosition = 0;

// Variable to store the return command
int returnCommand = 0;

void setup() {
  // Set the maximum speed and acceleration for the rotary stepper motor
  rotaryStepper.setMaxSpeed(500);
  rotaryStepper.setAcceleration(50);
  rotaryStepper.setSpeed(30);

  // Initialize the serial communication
  Serial.begin(9600);

  zeroPosition = rotaryStepper.currentPosition();
}

void loop() {
  if (targetRotaryPosition == 0) {
    // Read user input for the target position
    Serial.println("Enter target rotary position (degrees):");
    while (Serial.available() == 0) {
      // Wait for user input
    }
    targetRotaryPosition = Serial.parseInt();

    // Limit the target position to a maximum of 360 degrees
    if (targetRotaryPosition < -360) {
      targetRotaryPosition = -360;
    } else if (targetRotaryPosition > 360) {
      targetRotaryPosition = 360;
    }

    // Calculate the target step position based on the zero position
    int targetStepPosition = (targetRotaryPosition * ROTARY_STEPS_PER_DEGREE) + zeroPosition;

    // Move the rotary stepper motor to the specified target position
    rotaryStepper.moveTo(targetStepPosition);

    // Print target position
    Serial.print("Target rotary position: ");
    Serial.print(targetRotaryPosition);
    Serial.println(" degrees");

    // Send confirmation to Python
    Serial.println("Position set successfully");
  } else if (returnCommand == 0) {
    // Read user input for the return command
    Serial.println("Enter '0' to return to the original position:");
    while (Serial.available() == 0) {
      // Wait for user input
    }
    returnCommand = Serial.parseInt();

    if (returnCommand == 0) {
      // Move the rotary stepper motor back to the original position
      rotaryStepper.moveTo(zeroPosition);

      // Print original position
      Serial.print("Returning to original position: ");
      Serial.print(zeroPosition / ROTARY_STEPS_PER_DEGREE);
      Serial.println(" degrees");

      // Reset the target position and return command
      targetRotaryPosition = 0;
      returnCommand = -1;

      // Send confirmation to Python
      Serial.println("Returned to original position");
    }
  }

  // Run the rotary stepper motor until it reaches the target position or returns to the original position
  rotaryStepper.run();

  // Check if the stepper has reached the target position or the original position
  if (rotaryStepper.distanceToGo() == 0) {
    if (targetRotaryPosition != 0) {
      // Print current position after reaching the target position
      Serial.print("Reached target rotary position: ");
      Serial.print(targetRotaryPosition);
      Serial.println(" degrees");

      // Wait for the return command
      targetRotaryPosition = 0;

      // Send confirmation to Python
      Serial.println("Target position reached");
    } else if (returnCommand == 0) {
      // Print current position after returning to the original position
      Serial.print("Returned to original position: ");
      Serial.print(zeroPosition / ROTARY_STEPS_PER_DEGREE);
      Serial.println(" degrees");

      // Reset the return command
      returnCommand = -1;
    }
  }
}
