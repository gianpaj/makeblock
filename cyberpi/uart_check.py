# Minimum UART pin-pair check. Upload via mBlock 5 Upload Mode.
#
# Prereq: wire a 3.3V USB-serial adapter to the chosen GPIOs.
#     adapter RX  <- CyberPi TX   (UART_TX_PIN below)
#     adapter TX  -> CyberPi RX   (UART_RX_PIN below)
#     adapter GND -- CyberPi GND
#
# On your laptop, in another terminal:
#     pip install pyserial
#     python -m serial.tools.miniterm /dev/tty.usbserial-XXXX 115200
#
# Pass criteria:
#   1. "tick N" lines arrive on the laptop terminal, ~1/s.
#   2. Anything you type in miniterm shows up on the CyberPi LCD as "rx:...".
# If only (1) works, TX is on the right pin and RX isn't.
# If neither works, both pins are wrong (or wiring is off).
#
# Press B on the CyberPi to exit.

import cyberpi
import time
from machine import UART, Pin

UART_ID = 2
UART_TX_PIN = 32
UART_RX_PIN = 25

uart = UART(
    UART_ID,
    baudrate=115200,
    tx=Pin(UART_TX_PIN),
    rx=Pin(UART_RX_PIN),
    bits=8,
    parity=None,
    stop=1,
)

cyberpi.display.show_label("uart check", 16, 0, 0, index=0)
cyberpi.display.show_label(
    "TX={} RX={}".format(UART_TX_PIN, UART_RX_PIN), 12, 0, 30, index=1
)
cyberpi.display.show_label("B: exit", 12, 0, 100, index=3)

n = 0
last = time.ticks_ms()
while not cyberpi.controller.is_press("b"):
    now = time.ticks_ms()
    if time.ticks_diff(now, last) >= 1000:
        last = now
        uart.write("tick {}\n".format(n).encode("utf-8"))
        n += 1
    avail = uart.any()
    if avail:
        data = uart.read(avail)
        if data:
            try:
                text = data.decode("utf-8").strip()
                if text:
                    cyberpi.display.show_label(
                        "rx: " + text[-12:], 16, 0, 60, index=2
                    )
            except Exception:
                pass
    time.sleep(0.01)

cyberpi.display.show_label("done", 16, 0, 30, index=1)
