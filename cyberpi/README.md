# CyberPi bridge firmware

MicroPython script that runs on the Makeblock CyberPi (ESP32) on top of the
stock CyberPiOS. Implements the protocol in
[`../protocol/PROTOCOL.md`](../protocol/PROTOCOL.md).

## Layout

| File | Role |
| ---- | ---- |
| `main.py` | Entry point. Prints banner, calls `bridge.run()`. |
| `bridge.py` | UART read loop, JSON dispatch, deadman timer, sub scheduler. |
| `linereader.py` | Byte-stream → line framer used by `bridge.py`. |
| `chassis.py` | `drive(l, r)` / `stop()` over the `mbot2` module. Clamps. |
| `sensors.py` | `read_distance_cm()` over `mbuild.ultrasonic2`. Returns `None` on failure. |
| `test_bridge_smoke.py` | Desktop test harness. No `cyberpi`/`mbot2` deps. |
| `PINOUT.md` | CyberPi GPIO map; what's safe to use, what's claimed by the LCD/audio/I2C/PSRAM, and the rationale for the current UART pins. |

## Uploading via mBlock 5 / mBlock-Python Editor

1. Connect the CyberPi over USB.
2. Open mBlock 5 (or the standalone mBlock-Python Editor).
3. Switch the editor to **Upload Mode** (not Live Mode). Upload Mode replaces
   only the user script slot; **CyberPiOS stays intact** so `cyberpi`,
   `mbot2`, and `mbuild` keep working.
4. Upload `linereader.py`, `chassis.py`, `sensors.py`, and `bridge.py` first
   (helper modules), then `main.py` last so it becomes the boot script.
5. Power-cycle the mBot2. Within ~1 s of boot a single `hello` line should
   appear on the UART.

> Do **not** flash a PlatformIO/Arduino build. That overwrites CyberPiOS and
> the high-level Python modules disappear; you'd then have to re-flash
> CyberPiOS from Makeblock to recover.

## Bench testing without the CoreS3

You need a 3.3 V USB-serial adapter (FTDI, CP2102, CH340 at 3.3 V — **not**
5 V; the CyberPi pin header is 3.3 V).

Wire:

    adapter TX  -> CyberPi RX     (UART_RX_PIN in bridge.py)
    adapter RX  -> CyberPi TX     (UART_TX_PIN in bridge.py)
    adapter GND -> CyberPi GND

Then on your laptop:

    pip install pyserial
    python test_bridge_smoke.py /dev/tty.usbserial-XXXX

The script exercises ping / sub / drive / stop / deadman / malformed JSON /
unknown command and prints every line in both directions.

## Expected first-boot behavior

- Single line emitted on the UART within ~1 s:
  `{"evt":"hello","fw":"cyberpi-bridge","v":"0.1.0"}`
- Motors stopped.
- No further output until a `sub` or `ping` arrives.
- Any `drive` command makes motors run; if no further `drive`/`stop` arrives
  within **500 ms**, motors cut automatically.

## Pin assignments

`UART_TX_PIN` / `UART_RX_PIN` / `UART_ID` at the top of `bridge.py` are
placeholders pending hardware confirmation against the CyberPi pin header.
See [`PINOUT.md`](PINOUT.md) for the full GPIO map and the rationale for the
current picks. When you confirm or change the pins, update **both** files.
