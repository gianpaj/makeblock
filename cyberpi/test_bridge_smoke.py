"""
Desktop smoke test for the CyberPi bridge.

Does NOT import cyberpi / mbot2 / mbuild. Runs on a laptop with a USB-serial
adapter wired to the CyberPi UART header:

    adapter TX  -> CyberPi RX   (UART_RX_PIN in bridge.py)
    adapter RX  -> CyberPi TX   (UART_TX_PIN in bridge.py)
    adapter GND -> CyberPi GND

Usage:
    pip install pyserial
    python test_bridge_smoke.py /dev/tty.usbserial-XXXX

Power the mBot2 first so MicroPython is running bridge.run(). The script
exercises hello / ping / sub / drive / stop / deadman / bad-JSON / unknown-cmd
and prints every line in both directions.
"""

import json
import sys
import threading
import time

try:
    import serial
except ImportError:
    print("pyserial not installed. run: pip install pyserial")
    sys.exit(1)


def _reader(ser, stop_flag):
    buf = b""
    while not stop_flag["stop"]:
        chunk = ser.read(128)
        if not chunk:
            continue
        buf += chunk
        while b"\n" in buf:
            line, buf = buf.split(b"\n", 1)
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line.decode("utf-8"))
                print("<-", msg)
            except Exception:
                print("<- raw:", line)


def _send(ser, obj):
    ser.write((json.dumps(obj) + "\n").encode("utf-8"))
    print("->", obj)


def main():
    if len(sys.argv) < 2:
        print("usage: test_bridge_smoke.py <serial-port>")
        sys.exit(1)
    ser = serial.Serial(sys.argv[1], 115200, timeout=0.1)
    stop_flag = {"stop": False}
    t = threading.Thread(target=_reader, args=(ser, stop_flag), daemon=True)
    t.start()

    print("# waiting for hello...")
    time.sleep(1.0)

    print("\n# ping/pong")
    _send(ser, {"cmd": "ping", "id": 1})
    _send(ser, {"cmd": "ping", "id": 2})
    time.sleep(0.4)

    print("\n# subscribe to distance @ 5 Hz for 2 s")
    _send(ser, {"cmd": "sub", "topic": "dist", "hz": 5})
    time.sleep(2.0)

    print("\n# drive forward briefly, then stop")
    _send(ser, {"cmd": "drive", "l": 20, "r": 20})
    time.sleep(0.3)
    _send(ser, {"cmd": "stop"})
    time.sleep(0.3)

    print("\n# deadman: drive, then stay quiet >500 ms — motors should cut")
    _send(ser, {"cmd": "drive", "l": 30, "r": -30})
    time.sleep(1.0)

    print("\n# malformed JSON")
    ser.write(b"not json\n")
    time.sleep(0.3)

    print("\n# unknown command")
    _send(ser, {"cmd": "moonwalk"})
    time.sleep(0.3)

    print("\n# unsub")
    _send(ser, {"cmd": "unsub", "topic": "dist"})
    time.sleep(0.6)

    print("\n# done")
    stop_flag["stop"] = True
    ser.close()


if __name__ == "__main__":
    main()
