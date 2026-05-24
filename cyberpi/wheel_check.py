# Minimum upload-mode smoke test for the mBot2 wheels.
# Prop the bot on a book/stand first — the wheels will spin briefly.
# Upload via mBlock 5 / mBlock-Python Editor in Upload Mode, then press A
# on the CyberPi to run each phase. Nothing here is bridge-specific.

import cyberpi
import mbot2
import time


def wait_for_a(label):
    cyberpi.display.show_label(label, 16, 0, 30, index=1)
    while not cyberpi.controller.is_press("a"):
        time.sleep(0.02)
    while cyberpi.controller.is_press("a"):
        time.sleep(0.02)


cyberpi.display.show_label("wheel check", 16, 0, 0, index=0)

wait_for_a("A: fwd 20% 1s")
mbot2.drive_power(20, 20)
time.sleep(1)
mbot2.drive_power(0, 0)

wait_for_a("A: rev 20% 1s")
mbot2.drive_power(-20, -20)
time.sleep(1)
mbot2.drive_power(0, 0)

wait_for_a("A: spin L 1s")
mbot2.drive_power(-20, 20)
time.sleep(1)
mbot2.drive_power(0, 0)

cyberpi.display.show_label("done", 16, 0, 30, index=1)
