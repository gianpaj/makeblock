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

## Unknown: mBot2 shield mapping

The shield exposes:

- 2 encoder motor ports (EM1, EM2)
- 2 DC motor ports
- 4 servo / digital / analog / PWM ports (S1, S2, S3, S4)
- 1 mBuild passthrough port

…and consumes more ESP32 GPIOs to do it. The Python API (`mbot2.read_digital("S1")`,
`mbot2.servo_set(angle, 3)`, etc.) hides the pin numbers, and the Makeblock
support / education pages that used to document them now 302 to the homepage or
return 403. The PerfecXX repo's `firmware/` directory is binary blobs only.

**Practical consequence:** if you wire UART pins through the shield's pin
header, there's a real chance of colliding with whatever the shield uses for
S1–S4 / motors. The defensible candidates among GPIOs we know aren't claimed by
the CyberPi itself are **21, 22, 23, 25, 32** (regular GPIOs, not strap pins,
not PSRAM, not flash, not console UART).

## Current bridge UART picks

| Constant in `bridge.py` | Value | Note |
| --- | --- | --- |
| `UART_ID` | `2` | ESP32 has a free hardware UART2 (UART0 is the USB console). |
| `UART_TX_PIN` | `32` | Regular GPIO, no special function in CyberPi sources. |
| `UART_RX_PIN` | `25` | DAC1 — unused by CyberPi audio code. |

These are **not yet confirmed against the mBot2 shield silkscreen.** When you
verify (or substitute) the actual pins, update `bridge.py` and this table
together.
