# CyberPi side of the bridge. Protocol: ../protocol/PROTOCOL.md

import time
import ujson
from machine import UART, Pin

import chassis
import sensors
from linereader import LineReader

# CONFIRM against the CyberPi pin header before flashing. See PINOUT.md for
# the full GPIO map and why these are placeholders, not verified picks.
UART_ID = 2
UART_TX_PIN = 32
UART_RX_PIN = 25

UART_BAUD = 115200
DEADMAN_MS = 500
RX_LINE_MAX = 512
LOOP_SLEEP_MS = 5
DEBUG = False

FW_NAME = "cyberpi-bridge"
FW_VER = "0.1.0"
_VALID_TOPICS = ("dist",)


class Bridge:
    def __init__(self):
        self.uart = UART(
            UART_ID,
            baudrate=UART_BAUD,
            tx=Pin(UART_TX_PIN),
            rx=Pin(UART_RX_PIN),
            bits=8,
            parity=None,
            stop=1,
        )
        self._reader = LineReader(
            max_len=RX_LINE_MAX,
            on_overflow=lambda: self._err("line too long"),
        )
        self._last_cmd_ms = time.ticks_ms()
        self._motors_live = False
        self._subs = {}  # topic -> {"period": int, "next": ticks_ms}

    def _write(self, obj):
        try:
            self.uart.write((ujson.dumps(obj) + "\n").encode("utf-8"))
        except Exception as e:
            if DEBUG:
                print("write fail:", e)

    def hello(self):
        self._write({"evt": "hello", "fw": FW_NAME, "v": FW_VER})

    def _err(self, msg):
        self._write({"evt": "err", "msg": msg})

    def _poll_uart(self):
        n = self.uart.any()
        if not n:
            return
        chunk = self.uart.read(n)
        if not chunk:
            return
        for line in self._reader.feed(chunk):
            self._handle_line(line)

    def _handle_line(self, line):
        try:
            msg = ujson.loads(line)
        except Exception:
            self._err("bad json")
            return
        if not isinstance(msg, dict):
            self._err("not object")
            return
        cmd = msg.get("cmd")
        if cmd == "drive":
            self._cmd_drive(msg)
        elif cmd == "stop":
            self._cmd_stop()
        elif cmd == "ping":
            self._write({"evt": "pong", "id": msg.get("id")})
        elif cmd == "sub":
            self._cmd_sub(msg)
        elif cmd == "unsub":
            self._subs.pop(msg.get("topic"), None)
        else:
            self._err("unknown cmd")

    def _cmd_drive(self, msg):
        try:
            chassis.drive(msg.get("l", 0), msg.get("r", 0))
        except Exception:
            self._err("drive fail")
            return
        self._motors_live = True
        self._last_cmd_ms = time.ticks_ms()

    def _cmd_stop(self):
        try:
            chassis.stop()
        except Exception:
            pass
        self._motors_live = False
        self._last_cmd_ms = time.ticks_ms()

    def _cmd_sub(self, msg):
        topic = msg.get("topic")
        if topic not in _VALID_TOPICS:
            self._err("bad topic")
            return
        try:
            hz = int(msg.get("hz", 5))
        except Exception:
            self._err("bad hz")
            return
        if hz < 1:
            hz = 1
        elif hz > 20:
            hz = 20
        self._subs[topic] = {"period": 1000 // hz, "next": time.ticks_ms()}

    def _tick_subs(self):
        if not self._subs:
            return
        now = time.ticks_ms()
        for topic, s in self._subs.items():
            if time.ticks_diff(now, s["next"]) >= 0:
                s["next"] = time.ticks_add(now, s["period"])
                if topic == "dist":
                    cm = sensors.read_distance_cm()
                    if cm is not None:
                        self._write({"evt": "dist", "cm": cm, "t": now})

    def _check_deadman(self):
        if not self._motors_live:
            return
        if time.ticks_diff(time.ticks_ms(), self._last_cmd_ms) > DEADMAN_MS:
            try:
                chassis.stop()
            except Exception:
                pass
            self._motors_live = False

    def run(self):
        while True:
            self._poll_uart()
            self._check_deadman()
            self._tick_subs()
            time.sleep_ms(LOOP_SLEEP_MS)


def run():
    b = Bridge()
    b.hello()
    b.run()
