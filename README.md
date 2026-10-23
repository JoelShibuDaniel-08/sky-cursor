

https://github.com/user-attachments/assets/9fe4c0a6-a6f4-4833-a2f0-0107c6ad1a6e

<img width="720" height="1280" alt="Image" src="https://github.com/user-attachments/assets/750bbea3-da98-49a6-aa98-24d667f3d60f" />
# Sky Cursor: Bluetooth-Controlled Gesture Mouse

A wireless mouse controlled by hand gestures in the air. Hand motion moves the
cursor and finger bends trigger clicks.

## Hardware
- Arduino Nano
- MPU-6050 (accelerometer + gyroscope) for motion tracking
- Flex sensors for click gestures
- HC-05 Bluetooth module for wireless connection to the computer

## How it works
The MPU-6050 reads hand tilt/movement, and the flex sensors detect finger
bends. The Arduino combines these readings and sends cursor movement and
click commands over Bluetooth to the PC.

## Setup
1. Wire the components as shown in the circuit diagram (add image).
2. Upload `sky_cursor.ino` to the Arduino Nano using Arduino IDE.
3. Pair the HC-05 with your computer (default PIN 1234 or 0000).

## Demo
Photo and Video uploaded above 

## Author
Joel Shibu Daniel
