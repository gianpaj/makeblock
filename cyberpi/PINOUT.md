# CyberPi GPIO map

Reference for picking pins for the bridge UART (or any future direct
`machine.Pin` / `machine.UART` use). Everything here is derived from sources I
could verify — the mBot2 shield mapping is **not** here because no public source
I could reach documents it.

## Module

CyberPi uses **ESP32-WROVER-B** (8 MB SPI flash + 8 MB PSRAM). See the spec
table in `PerfecXX/mBot2/example/micropython/cyberpi/readme.md`.

## Reserved by the ESP32-WROVER-B module itself

| GPIO | Reason |
| ---- | ------ |
| 6–11 | SPI flash |
| 16, 17 | PSRAM (CSB, SPI_CLK on WROVER-B) — **NEVER use, even though these are the stock UART2 defaults** |
| 1, 3 | USB-serial console (UART0) |
| 0, 15 | Strap pins (boot-mode selection) |
| 34, 36–39 | Input-only on ESP32 |

## Used by CyberPi internals

Sourced from the Makeblock Arduino library at
`CyberPi-Library-for-Arduino/lib/cyberpi/src/`:

| GPIO | Function | Source |
| ---- | -------- | ------ |
| 2  | LCD MOSI | `lcd/lcd.h:130` |
| 4  | LCD CLK  | `lcd/lcd.h:132` |
| 12 | LCD CS   | `lcd/lcd.h:133` |
| 13 | Microphone I2S BCK | `cyberpi.cpp:449` |
| 14 | Microphone I2S WS  | `cyberpi.cpp:450` |
| 18 | I2C SCL (gyro / AW9523B / audio codec) | `i2c/i2c.h:6` |
| 19 | I2C SDA | `i2c/i2c.h:7` |
| 26 | LCD MISO **and** DAC2 audio out | `lcd/lcd.h:131`, `cyberpi.cpp:355` |
| 27 | Font-ROM (GT30L24A3W) chip select | `lcd/lcd.c:11` |
| 33 | Light sensor (analog) | `cyberpi.cpp:62` |
| 35 | Microphone I2S data in (input-only) | `cyberpi.cpp:452` |

UI inputs (joystick, A/B/menu buttons, LCD DC/RST/BCKL) live on an AW9523B I2C
GPIO expander (`io/aw9523b.h`), not on ESP32 pins, so they don't consume real
GPIOs beyond the I2C bus above.

DAC1 (GPIO 25) is **not** enabled — `i2s_set_dac_mode(I2S_DAC_CHANNEL_RIGHT_EN)`
in `cyberpi.cpp` only turns on the right channel (DAC2 = GPIO 26).

## Empirical finding: shield ports are behind a secondary MCU

Original assumption was that S1/S2 might be direct ESP32 GPIOs we could
reclaim for `machine.UART`. **They aren't.** `cyberpi/scan_ports.py` toggled
each port via `mbot2.write_digital` while sampling every candidate ESP32 GPIO
(5, 15, 21, 22, 23, 25, 32, 34, 36, 39) with `machine.Pin(N, Pin.IN)`. No GPIO
followed either S1 or S2. That means the shield carries its own MCU which
takes commands from the CyberPi (over I2C, going by GPIOs 18/19) and drives
S1–S4 / motors on its own pins. The ESP32 never sees those lines.

The bare CyberPi has no general-purpose pin header either — only USB-C, the
HOME button, and the mBuild port. The original spec's "free UART exposed on
the CyberPi pin header" was incorrect; there's no such header to expose
anything on.

## What this rules in and out

- **`machine.UART(tx=Pin(N), rx=Pin(M))` on S1/S2** — dead. Pins aren't on the ESP32.
- **`machine.UART` on the mBuild port** — possible only if we can identify
  the underlying ESP32 GPIOs (the mBuild bus is described by Makeblock as
  "serial communication" but the GPIO mapping isn't in any source I can
  reach). Sharing the bus with the existing ultrasonic would require
  speaking the mBuild framing, not raw JSON.
- **USB-C** — the CyberPi's Type-C exposes ESP32 UART0 via the onboard CH340.
  Reachable from the CoreS3 if it can act as a USB host with a CH340 driver,
  and if we tolerate CyberPiOS's stray boot/console output on the same line.
- **Hardware mod** — solder a thin wire to an ESP32 test pad inside the
  CyberPi case (e.g. GPIO 21/22/23) and run it out. Preserves the original
  architecture entirely; costs an hour of physical work.

## Current bridge UART picks

The constants in `bridge.py` (`UART_ID=2`, `UART_TX_PIN=32`, `UART_RX_PIN=25`)
are now **stale** — they assume the external pin header that doesn't exist.
They'll be revisited once we pick between mBuild / USB / hardware-mod paths.
