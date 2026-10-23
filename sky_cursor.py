"""
Sky Cursor - PC-side receiver
Reads data sent by the Arduino Nano (Sky_Cursor.ino) over the HC-05
Bluetooth module and controls the mouse on the computer.

The Arduino sends one line per reading, in this format:
    CURSOR_X:<float>,CURSOR_Y:<float>,ACTION:<Move|Left Click|Right Click>
and "Device is OFF" while the glove's power button has it switched off.

Install:  pip install pyserial pyautogui
Run:      python sky_cursor.py
"""

import sys
import serial
import pyautogui

# ---- Settings (change these) -------------------------------------------
PORT = "COM5"        # HC-05 outgoing COM port (Windows). Linux: /dev/rfcomm0
BAUD = 9600          # Must match bluetooth.begin(9600) in the Arduino code
SCALE = 0.05         # Lower = slower cursor. The Arduino values are large
                     # (30 to 327), so they are scaled down here.
MAX_STEP = 40        # Max pixels moved per reading (keeps cursor controllable)
INVERT_X = False     # Set True if the cursor moves left when you tilt right
INVERT_Y = False     # Set True if the cursor moves up when you tilt down
SWAP_XY = False      # Set True if tilt axes are swapped for your glove mounting
# ------------------------------------------------------------------------

pyautogui.FAILSAFE = True   # move mouse to a screen corner to stop
pyautogui.PAUSE = 0         # no delay between actions


def parse_line(line):
    """Parse 'CURSOR_X:1.5,CURSOR_Y:-3.0,ACTION:Move'.
    Returns (x, y, action) or None if the line is not a valid reading."""
    line = line.strip()
    if not line.startswith("CURSOR_X:"):
        return None  # e.g. "Device is OFF" or a partial/garbled line
    try:
        fields = dict(part.split(":", 1) for part in line.split(","))
        x = float(fields["CURSOR_X"])
        y = float(fields["CURSOR_Y"])
        action = fields["ACTION"].strip()
        return x, y, action
    except (ValueError, KeyError):
        return None


def clamp(value, limit):
    return max(-limit, min(limit, value))


def main():
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
    except serial.SerialException as e:
        print(f"Could not open {PORT}: {e}")
        print("Check that the HC-05 is paired and the COM port is correct.")
        sys.exit(1)

    print(f"Connected to {PORT}. Turn the glove on with its power button.")
    print("Press Ctrl+C to quit.")

    held = None  # which mouse button is currently held: None, "left", "right"

    def set_button(wanted):
        """Hold the wanted button (or release all if None)."""
        nonlocal held
        if wanted == held:
            return
        if held is not None:
            pyautogui.mouseUp(button=held)
        if wanted is not None:
            pyautogui.mouseDown(button=wanted)
        held = wanted

    try:
        while True:
            raw = ser.readline().decode("utf-8", errors="ignore")
            parsed = parse_line(raw)
            if parsed is None:
                continue

            x, y, action = parsed

            if SWAP_XY:
                x, y = y, x
            if INVERT_X:
                x = -x
            if INVERT_Y:
                y = -y

            dx = int(clamp(x * SCALE, MAX_STEP))
            dy = int(clamp(y * SCALE, MAX_STEP))
            if dx or dy:
                pyautogui.moveRel(dx, dy)

            # Clicks: button stays pressed while the finger stays bent,
            # so holding a bend lets you drag.
            if action == "Left Click":
                set_button("left")
            elif action == "Right Click":
                set_button("right")
            else:
                set_button(None)

    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        set_button(None)
        ser.close()


if __name__ == "__main__":
    main()
