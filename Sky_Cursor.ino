#include <Wire.h>         // For I2C communication with MPU6050
#include <SoftwareSerial.h>

// Pin Definitions
#define FLEX_LEFT_PIN A0       // Flex sensor for left-click
#define FLEX_RIGHT_PIN A1      // Flex sensor for right-click
#define MPU_ADDR 0x68          // I2C address of MPU6050
#define BLUETOOTH_TX_PIN 2     // Arduino TX pin for Bluetooth module
#define BLUETOOTH_RX_PIN 3     // Arduino RX pin for Bluetooth module
#define POWER_BUTTON_PIN 4     // Power button pin
// Bluetooth communication
SoftwareSerial bluetooth(BLUETOOTH_RX_PIN, BLUETOOTH_TX_PIN);

// Variables for sensors
int flexLeftValue;             // Flex sensor value for left-click
int flexRightValue;            // Flex sensor value for right-click
int16_t accX, accY, accZ;      // Accelerometer readings
float cursorSpeedX, cursorSpeedY;

// Thresholds
const int flexThresholdLeftClick = 600;  // Threshold for left-click
const int flexThresholdRightClick = 600; // Threshold for right-click
const int cursorThreshold = 3000;        // Sensitivity threshold for accelerometer

// Cursor control scaling factor
const float sensitivity = 0.01;

// Power button state
bool isDeviceOn = false;

void setup() {
  // Initialize Serial Monitor and Bluetooth
  Serial.begin(9600);
  bluetooth.begin(9600);

  // Initialize I2C communication for MPU6050
  Wire.begin();
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x6B);        // Access power management register
  Wire.write(0);           // Wake up the MPU6050
  Wire.endTransmission();

  // Pin Modes
  pinMode(FLEX_LEFT_PIN, INPUT);
  pinMode(FLEX_RIGHT_PIN, INPUT);
  pinMode(POWER_BUTTON_PIN, INPUT_PULLUP); // Button with internal pull-up resistor

  Serial.println("Bluetooth Glove Ready");
}

void loop() {
  // Check power button state
  static bool lastButtonState = HIGH;
  bool currentButtonState = digitalRead(POWER_BUTTON_PIN);

  if (currentButtonState == LOW && lastButtonState == HIGH) {
    isDeviceOn = !isDeviceOn; // Toggle power state
    delay(300);               // Debounce delay
  }
  lastButtonState = currentButtonState;

  // If device is off, stop processing
  if (!isDeviceOn) {
    Serial.println("Device is OFF");
    bluetooth.println("Device is OFF");
    delay(500);
    return;
  }

  // Read Flex Sensor Values
  flexLeftValue = analogRead(FLEX_LEFT_PIN);
  flexRightValue = analogRead(FLEX_RIGHT_PIN);

  // Read Accelerometer Data
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B);        // Starting register for accelerometer data
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_ADDR, 6, true); // Request 6 bytes of data

  accX = Wire.read() << 8 | Wire.read();
  accY = Wire.read() << 8 | Wire.read();
  accZ = Wire.read() << 8 | Wire.read();

  // Convert accelerometer data to cursor movement
  cursorSpeedX = (float)accX * sensitivity;
  cursorSpeedY = (float)accY * sensitivity;

  // Apply a deadzone threshold to avoid small unintentional movements
  if (abs(accX) < cursorThreshold) cursorSpeedX = 0;
  if (abs(accY) < cursorThreshold) cursorSpeedY = 0;

  // Determine Actions for Flex Sensors
  String action = "Move";
  if (flexLeftValue > flexThresholdLeftClick) {
    action = "Left Click";
  }
  if (flexRightValue > flexThresholdRightClick) {
    action = "Right Click";
  }

  // Prepare data string
  String data = "CURSOR_X:" + String(cursorSpeedX) +
                ",CURSOR_Y:" + String(cursorSpeedY) +
                ",ACTION:" + action;

  // Send data via Bluetooth
  bluetooth.println(data);

  // Debug output to Serial Monitor
  Serial.println(data);

  // Small delay to avoid flooding
  delay(50);
}
