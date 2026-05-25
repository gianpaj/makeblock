# Empirical scan: which ESP32 GPIO (if any) tracks the shield's S1/S2 port?
# Toggles each port via mbot2.write_digital while sampling candidate ESP32
# GPIOs via machine.Pin(N, Pin.IN). A GPIO that follows the level is the
# underlying pin and is usable for machine.UART. If nothing follows, the
# port is behind a shield-side MCU and Option 2 is dead.
#
# Upload via mBlock 5 Upload Mode. Press A to scan, B to exit.
# Results are shown on the LCD AND printed (visible in mBlock's terminal).
# No motor activity, no UART activity.

import cyberpi
import mbot2
import time
from machine import Pin

# ESP32 GPIOs the CyberPi sources don't claim, that aren't flash/PSRAM/
# console/strap-critical, and that are safe to drive Pin.IN on.
CANDIDATES = [5, 15, 21, 22, 23, 25, 32, 34, 36, 39]
PORTS = ("S1", "S2")
SETTLE_MS = 100


def sample_all():
    out = {}
    for g in CANDIDATES:
        try:
            out[g] = Pin(g, Pin.IN).value()
        except Exception:
            out[g] = None
    return out


def scan_port(port):
    mbot2.write_digital(0, port)
    time.sleep_ms(SETTLE_MS)
    lo1 = sample_all()
    mbot2.write_digital(1, port)
    time.sleep_ms(SETTLE_MS)
    hi = sample_all()
    mbot2.write_digital(0, port)
    time.sleep_ms(SETTLE_MS)
    lo2 = sample_all()
    hits = []
    for g in CANDIDATES:
        if lo1[g] is None:
            continue
        if lo1[g] == lo2[g] and lo1[g] != hi[g]:
            hits.append(g)
    return hits


def wait_press(btn):
    while not cyberpi.controller.is_press(btn):
        time.sleep_ms(20)
    while cyberpi.controller.is_press(btn):
        time.sleep_ms(20)


cyberpi.display.show_label("port scan", 16, 0, 0, index=0)
cyberpi.display.show_label("A: scan  B: exit", 12, 0, 30, index=1)

wait_press("a")
cyberpi.display.show_label("scanning S1...", 12, 0, 30, index=1)

results = {}
for port in PORTS:
    results[port] = scan_port(port)
    cyberpi.display.show_label("scanned " + port, 12, 0, 30, index=1)

y = 50
for port in PORTS:
    hits = results[port]
    msg = "{}: {}".format(port, ",".join(str(h) for h in hits) if hits else "none")
    print(msg)
    cyberpi.display.show_label(msg, 14, 0, y, index=(2 if port == "S1" else 3))
    y += 25

cyberpi.display.show_label("done.  B: exit", 12, 0, 110, index=4)
wait_press("b")
