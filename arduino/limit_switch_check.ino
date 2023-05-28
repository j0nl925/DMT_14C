// Define the pins for the limit switches
const uint8_t TOP_LIMIT_SWITCH = 7;
const uint8_t BOTTOM_LIMIT_SWITCH = 8;

void setup() {
  // Configure the limit switch pins as inputs with pull-up resistors
  pinMode(TOP_LIMIT_SWITCH, INPUT_PULLUP);
  pinMode(BOTTOM_LIMIT_SWITCH, INPUT_PULLUP);
  
  // Initialize serial communication
  Serial.begin(9600);
}

void loop() {
  // Read the state of the limit switches
  int topSwitchState = digitalRead(TOP_LIMIT_SWITCH);
  int bottomSwitchState = digitalRead(BOTTOM_LIMIT_SWITCH);

  // Print the state of the limit switches to the Serial Monitor
  Serial.print("Top limit switch state: ");
  Serial.println(topSwitchState == HIGH ? "Unpressed" : "Pressed");
  
  Serial.print("Bottom limit switch state: ");
  Serial.println(bottomSwitchState == HIGH ? "Unpressed" : "Pressed");

  // Wait for a short period of time before reading the switch state again
  delay(500);
}
