# Minimum ultrasonic-sensor smoke test. Upload via mBlock 5 Upload Mode.
# Plug Ultrasonic Sensor 2 into the mBuild port chain on the mBot2 shield.
# Wave a hand / book in front; the LCD shows the live cm reading.
# Press B to exit.

import cyberpi
import mbuild
import time

cyberpi.display.show_label("ultrasonic", 16, 0, 0, index=0)
cyberpi.display.show_label("B: exit", 16, 0, 80, index=2)

while not cyberpi.controller.is_press("b"):
    cm = mbuild.ultrasonic2.get(index=1)
    cyberpi.display.show_label("{} cm   ".format(cm), 24, 0, 30, index=1)
    time.sleep(0.1)

cyberpi.display.show_label("done", 16, 0, 30, index=1)
