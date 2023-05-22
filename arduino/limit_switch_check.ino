// Define the pins for the limit switches
const uint8_t LINEAR_LIMIT_SWITCH = 7;
const uint8_t ROTARY_LIMIT_SWITCH = 8;

void setup() {
  // Configure the limit switch pins as inputs with pull-up resistors
  pinMode(LINEAR_LIMIT_SWITCH, INPUT_PULLUP);
  pinMode(ROTARY_LIMIT_SWITCH, INPUT_PULLUP);
  
  // Initialize serial communication
  Serial.begin(9600);
}

void loop() {
  // Read the state of the limit switches
  int linearSwitchState = digitalRead(LINEAR_LIMIT_SWITCH);
  int rotarySwitchState = digitalRead(ROTARY_LIMIT_SWITCH);

  // Print the state of the limit switches to the Serial Monitor
  Serial.print("Linear limit switch state: ");
  Serial.println(linearSwitchState == HIGH ? "Unpressed" : "Pressed");
  
  Serial.print("Rotary limit switch state: ");
  Serial.println(rotarySwitchState == HIGH ? "Unpressed" : "Pressed");

  // Wait for a short period of time before reading the switch state again
  delay(500);
}
