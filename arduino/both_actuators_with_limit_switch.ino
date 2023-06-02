#include <AccelStepper.h>

// Define the pins for the linear actuator
const uint8_t LINEAR_STEP_PIN = 3;
const uint8_t LINEAR_DIR_PIN = 2;
const uint8_t BOTTOM_LIMIT_SWITCH = 7;
const uint8_t TOP_LIMIT_SWITCH = 8;

// Define the pins for the rotary stepper motor
const uint8_t ROTARY_STEP_PIN = 9;
const uint8_t ROTARY_DIR_PIN = 10;

// Define the resolution of the linear actuator and rotary stepper motor
const float LINEAR_RESOLUTION = 1.8;
const float ROTARY_RESOLUTION = 1.8;

// Define the stroke of the linear actuator
const float LINEAR_STROKE = 100.0;

// Define the number of steps per revolution for the linear actuator and rotary stepper motor
const int LINEAR_STEPS_PER_REVOLUTION = 200;
const int ROTARY_STEPS_PER_REVOLUTION = 200;

// Define the number of steps per mm for the linear actuator and rotary stepper motor
const float LINEAR_STEPS_PER_MM = LINEAR_STEPS_PER_REVOLUTION / LINEAR_STROKE;
const float ROTARY_STEPS_PER_DEGREE = ROTARY_STEPS_PER_REVOLUTION / 360.0;

// Define the linear actuator and rotary stepper motor
AccelStepper linearActuator(AccelStepper::DRIVER, LINEAR_STEP_PIN, LINEAR_DIR_PIN);
AccelStepper rotaryStepper(AccelStepper::DRIVER, ROTARY_STEP_PIN, ROTARY_DIR_PIN);

// Define initial positions for the linear actuator and rotary stepper motor
int linPosition = 0;
int rotPosition = 0;

void setup() {
  // Configure the limit switch pins as inputs with pull-up resistors
  pinMode(BOTTOM_LIMIT_SWITCH, INPUT_PULLUP);
  pinMode(TOP_LIMIT_SWITCH, INPUT_PULLUP);

  // Set the maximum speed and acceleration for the linear actuator and rotary stepper motor
  linearActuator.setMaxSpeed(500);
  linearActuator.setAcceleration(500);
  linearActuator.setSpeed(400);
  rotaryStepper.setMaxSpeed(500);
  rotaryStepper.setAcceleration(500);
  rotaryStepper.setSpeed(400);

  // Initialize the serial communication
  Serial.begin(9600);
  
  // Move linear actuator to position 500 on startup
  linearActuator.moveTo(500);
  while (linearActuator.distanceToGo() != 0) {
    linearActuator.run();
  }
  
  // Move linear actuator to position 200 after reaching the top limit switch
  int targetPosition0 = 10000;
  linearActuator.moveTo(targetPosition0);
  while (linearActuator.distanceToGo() != 0) {
    if (digitalRead(TOP_LIMIT_SWITCH) == 1) {
      // Stop the linear actuator when the top limit switch is pressed
      linearActuator.stop();
      linearActuator.setCurrentPosition(0);
      linearActuator.moveTo(200);
      while (linearActuator.distanceToGo() != 0) {
        linearActuator.run();
      }
    }
    else if (digitalRead(BOTTOM_LIMIT_SWITCH) == 1) {
      // Stop the linear actuator when the bottom limit switch is pressed
      linearActuator.stop();
      linearActuator.setCurrentPosition(0);
      linearActuator.moveTo(-1 * targetPosition0);
    }
    linearActuator.run();
  }
}

void loop() {
  // Check if the bottom limit switch is pressed
  // read user input for linear and rotary positions
  Serial.println("Enter linear position (mm):");
  while (Serial.available() == 0) {
    // Wait for user input
  }
  linPosition = Serial.parseFloat();
  
  Serial.println("Enter rotary position (degrees):");
  while (Serial.available() == 0) {
    // Wait for user input
  }
  rotPosition = Serial.parseFloat();

  // Move linear actuator to the specified position
  int targetLinearPosition = linPosition * LINEAR_STEPS_PER_MM;
  linearActuator.moveTo(targetLinearPosition);

  // Move rotary stepper motor to the specified position
  int targetRotaryPosition = rotPosition * ROTARY_STEPS_PER_DEGREE;
  rotaryStepper.moveTo(targetRotaryPosition);

  // Run both steppers until they reach their respective targets
  while (linearActuator.distanceToGo() != 0 || rotaryStepper.distanceToGo() != 0) {
    if (digitalRead(BOTTOM_LIMIT_SWITCH) == 1) {
      // Move linear actuator to position 0
      linearActuator.stop();
      linearActuator.setCurrentPosition(0); // Reset the actuator's position to 0
      linearActuator.moveTo(-1 * targetLinearPosition);
    }
    else if (digitalRead(TOP_LIMIT_SWITCH) == 1) {
      // Stop the linear actuator when the top limit switch is pressed
      linearActuator.stop();
      linearActuator.setCurrentPosition(0);
      linearActuator.moveTo(200);
      while (linearActuator.distanceToGo() != 0) {
        linearActuator.run();
      }
    }

    // Run the rotary stepper motor
    rotaryStepper.run();
    // Run the linear actuator
    linearActuator.run();
  }

  // Print current positions
  Serial.print("Current linear position: ");
  Serial.print(linearActuator.currentPosition() / LINEAR_STEPS_PER_MM);
  Serial.println(" mm");
  
  Serial.print("Current rotary position: ");
  Serial.print(rotaryStepper.currentPosition() / ROTARY_STEPS_PER_DEGREE);
  Serial.println(" degrees");

  // Send confirmation to Python
  Serial.println("OK");

  while (Serial.available() > 0) {
    linPosition = Serial.parseFloat();
    rotPosition = Serial.parseFloat();
  }
}
