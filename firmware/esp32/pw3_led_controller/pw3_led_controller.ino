// ============================================================
// MindSpark ROS2 Training Module
// PW3 - ESP32 LED Controller
//
// Communication: USB Serial
// Baud Rate    : 115200
//
// Commands:
// L = LEFT   (Red LED)
// C = CENTRE (Yellow LED)
// R = RIGHT  (Green LED)
// N = NONE   (All LEDs OFF)
// ============================================================

const int redLED = 25;
const int yellowLED = 26;
const int greenLED = 27;

// ------------------------------------------------------------
// Turn off all LEDs
// ------------------------------------------------------------

void allLEDsOff() {
  digitalWrite(redLED, LOW);
  digitalWrite(yellowLED, LOW);
  digitalWrite(greenLED, LOW);
}

// ------------------------------------------------------------
// Setup
// ------------------------------------------------------------

void setup() {

  Serial.begin(115200);

  pinMode(redLED, OUTPUT);
  pinMode(yellowLED, OUTPUT);
  pinMode(greenLED, OUTPUT);

  allLEDsOff();

  Serial.println("PW3 ESP32 LED Controller Ready");
}

// ------------------------------------------------------------
// Main Loop
// ------------------------------------------------------------

void loop() {

  if (Serial.available() > 0) {

    char command = Serial.read();

    // Ignore newline and carriage return
    if (command == '\n' || command == '\r') {
      return;
    }

    allLEDsOff();

    switch (command) {

      case 'L':
      case 'l':
        digitalWrite(redLED, HIGH);
        Serial.println("LEFT - RED LED ON");
        break;

      case 'C':
      case 'c':
        digitalWrite(yellowLED, HIGH);
        Serial.println("CENTER - YELLOW LED ON");
        break;

      case 'R':
      case 'r':
        digitalWrite(greenLED, HIGH);
        Serial.println("RIGHT - GREEN LED ON");
        break;

      case 'N':
      case 'n':
        Serial.println("NONE - ALL LEDs OFF");
        break;

      default:
        Serial.println("Invalid command");
        break;
    }
  }
}
