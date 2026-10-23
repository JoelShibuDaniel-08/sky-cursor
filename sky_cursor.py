"""
Sky Cursor - PC-side receiver
Reads cursor movement and click data sent by the Arduino Nano over the
HC-05 Bluetooth module and controls the mouse on the computer.

Expected serial line format from the Arduino (one line per reading):
    dx,dy,left,right
Example:
    5,-3,0,1
  dx, dy : cursor movement in pixels (positive = right / down)
  left   : 1 if left-click flex sensor is bent, else 0
  right  : 1 if right-click flex sensor is bent, else 0

Install:  pip install pyserial pyautogui
Run:      python sky_cursor.py
"""

import sys
import serial
import pyautogui

# ---- Settings (change these) -------------------------------------------
PORT = "COM5"        # HC-05 outgoing COM port (Windows). Linux: /dev/rfcomm0
BAUD = 9600          # HC-05 default baud rate
SENSITIVITY = 1.0    # multiply movement (increase for faster cursor)
DEADZONE = 1         # ignore tiny movements (reduces jitter)
# ------------------------------------------------------------------------

pyautogui.FAILSAFE = True   # move mouse to a screen corner to stop
pyautogui.PAUSE = 0         # no delay between actions


def parse_line(line):
    """Turn 'dx,dy,left,right' into four ints. Return None if invalid."""
    parts = line.strip().split(",")
    if len(parts) != 4:
        return None
    try:
        return [int(p) for p in parts]
    except ValueError:
        return None


def main():
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
    except serial.SerialException as e:
        print(f"Could not open {PORT}: {e}")
        print("Check that the HC-05 is paired and the COM port is correct.")
        sys.exit(1)

    print(f"Connected to {PORT}. Move your hand to control the cursor.")
    print("Press Ctrl+C to quit.")

    left_down = False
    right_down = False

    try:
        while True:
            raw = ser.readline().decode("utf-8", errors="ignore")
            data = parse_line(raw)
            if data is None:
                continue

            dx, dy, left, right = data

            # Cursor movement
            if abs(dx) > DEADZONE or abs(dy) > DEADZONE:
                pyautogui.moveRel(dx * SENSITIVITY, dy * SENSITIVITY)

            # Left click / drag: press on bend, release when straightened
            if left and not left_down:
                pyautogui.mouseDown(button="left")
                left_down = True
            elif not left and left_down:
                pyautogui.mouseUp(button="left")
                left_down = False

            # Right click
            if right and not right_down:
                pyautogui.mouseDown(button="right")
                right_down = True
            elif not right and right_down:
                pyautogui.mouseUp(button="right")
                right_down = False

    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        if left_down:
            pyautogui.mouseUp(button="left")
        if right_down:
            pyautogui.mouseUp(button="right")
        ser.close()


if __name__ == "__main__":
    main()
