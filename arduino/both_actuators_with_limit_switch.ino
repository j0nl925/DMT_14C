#include <AccelStepper.h>

// Common definitions
#define MAX_SPEED 500
#define ACCELERATION 500
#define SPEED 400

// Rotary actuator definitions
#define ROTARY_STEP_PIN 4
#define ROTARY_DIR_PIN 5
#define ROTARY_STEPS_PER_REVOLUTION 200
#define ROTARY_STEPS_PER_DEGREE (ROTARY_STEPS_PER_REVOLUTION / 360.0)
AccelStepper rotaryStepper(AccelStepper::DRIVER, ROTARY_STEP_PIN, ROTARY_DIR_PIN);

// Linear actuator definitions
#define LINEAR_STEP_PIN 3
#define LINEAR_DIR_PIN 2
#define BOTTOM_LIMIT_SWITCH 7
#define TOP_LIMIT_SWITCH 8
#define LINEAR_RESOLUTION 1.8
#define LINEAR_STROKE 100.0
#define LINEAR_STEPS_PER_REVOLUTION 200
#define LINEAR_STEPS_PER_MM (LINEAR_STEPS_PER_REVOLUTION / LINEAR_STROKE)
AccelStepper linearActuator(AccelStepper::DRIVER, LINEAR_STEP_PIN, LINEAR_DIR_PIN);

// State control
#define STATE_WAITING 0
#define STATE_MOVE_LINEAR 1
#define STATE_MOVE_ROTARY 2
int state = STATE_WAITING;

// Position variables
int targetRotaryPosition = 0;
int linPosition = 0;
int zeroPosition = 0;

void setup() {
  pinMode(BOTTOM_LIMIT_SWITCH, INPUT_PULLUP);
  pinMode(TOP_LIMIT_SWITCH, INPUT_PULLUP);

  rotaryStepper.setMaxSpeed(MAX_SPEED);
  rotaryStepper.setAcceleration(ACCELERATION);
  rotaryStepper.setSpeed(SPEED);

  linearActuator.setMaxSpeed(MAX_SPEED);
  linearActuator.setAcceleration(ACCELERATION);
  linearActuator.setSpeed(SPEED);

  Serial.begin(9600);

  zeroPosition = rotaryStepper.currentPosition();
  
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
  if (state == STATE_WAITING) {
    // Read user input for positions
    if (Serial.available() > 0) {
      linPosition = Serial.parseInt();
      targetRotaryPosition = Serial.parseInt();
      // First, we move the linear actuator
      state = STATE_MOVE_LINEAR;
    }
  } else if (state == STATE_MOVE_LINEAR) {
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
    // Then, we move the rotary actuator
    if (linearActuator.distanceToGo() == 0) {
      state = STATE_MOVE_ROTARY;
    }
  } else if (state == STATE_MOVE_ROTARY) {
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
    // When it finishes, go back to the waiting state
    if (rotaryStepper.distanceToGo() == 0) {
      state = STATE_WAITING;
    }
  }

  // Run the stepper motors
  rotaryStepper.run();
  linearActuator.run();
}
