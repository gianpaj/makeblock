# mBot2 ↔ StackChan serial bridge — wire protocol

Single source of truth. Both sides MUST conform to this document; if the code
disagrees with this file, the file wins and the code is a bug.

## Transport

- Physical layer: UART, 3.3 V logic, single twisted pair plus common ground.
- Wiring: CyberPi `TX` → CoreS3 `RX`; CyberPi `RX` → CoreS3 `TX`; shared `GND`.
- Line settings: **115200 baud, 8 data bits, no parity, 1 stop bit (8N1)**.
- No hardware flow control. No DTR/RTS handshake.
- Framing: **one UTF-8 JSON object per line, terminated by `\n` (0x0A)**.
  - `\r` (0x0D) is tolerated and ignored on receive.
  - Lines longer than 512 bytes are dropped and the receiver SHOULD emit
    `{"evt":"err","msg":"line too long"}`.
- Endianness / numeric format: JSON only. No binary frames.

## Roles

- **CoreS3** is the controller. It issues `cmd` messages.
- **CyberPi** is the actuator/sensor node. It issues `evt` messages.

A message is one of:
- `{"cmd": "...", ...}` — controller → actuator
- `{"evt": "...", ...}` — actuator → controller

A message with neither key, or with an unknown value, is malformed.

## Commands (CoreS3 → CyberPi)

### `drive`
```json
{"cmd": "drive", "l": -100, "r": 100}
```
- `l`, `r`: integers in `[-100, 100]`. Percent of full wheel speed. Sign
  indicates direction (`+` forward, `-` reverse).
- Values outside the range are clamped, not rejected.
- The command persists: motors hold the last commanded speed until the next
  `drive`, a `stop`, or the deadman timeout (see Safety).

### `stop`
```json
{"cmd": "stop"}
```
- Equivalent to `{"cmd":"drive","l":0,"r":0}`. Also resets the deadman timer.

### `ping`
```json
{"cmd": "ping", "id": 42}
```
- `id`: any integer chosen by the sender. The actuator MUST reply with
  `{"evt":"pong","id":42}` — the same `id` echoed back.

### `sub`
```json
{"cmd": "sub", "topic": "dist", "hz": 10}
```
- Starts streaming the named topic at `hz` Hz.
- `hz`: integer in `[1, 20]`. Out-of-range values are clamped.
- Currently supported topics: `dist`.
- A second `sub` for an already-subscribed topic re-arms the timer at the new
  rate.

### `unsub`
```json
{"cmd": "unsub", "topic": "dist"}
```
- Stops streaming the named topic. Unknown topics are a no-op.

## Events (CyberPi → CoreS3)

### `hello`
```json
{"evt": "hello", "fw": "cyberpi-bridge", "v": "0.1.0"}
```
- Emitted exactly once, shortly after boot, before any other event.

### `pong`
```json
{"evt": "pong", "id": 42}
```
- Reply to `ping`. Echoes the request's `id` field verbatim.

### `dist`
```json
{"evt": "dist", "cm": 42.7, "t": 12345}
```
- Ultrasonic distance reading in centimetres.
- `t`: monotonic millisecond timestamp from the CyberPi (`time.ticks_ms()`).
  Not wall-clock; suitable for delta measurements only.
- Emitted only while subscribed via `sub topic=dist`.
- If the sensor read fails for any reason, the event for that tick is skipped
  (no `null` is sent).

### `err`
```json
{"evt": "err", "msg": "bad json"}
```
- Sent in response to:
  - JSON parse failure
  - top-level value not an object
  - unknown `cmd`
  - unknown `topic` in `sub`
  - line over 512 bytes
  - any handler-level failure that would otherwise crash
- The bridge MUST NOT terminate or stop polling because of any input.

## Safety

- **Deadman timeout: 500 ms.** If the bridge has commanded the motors live
  (last command was a non-zero `drive`) and no `drive` or `stop` has arrived
  within 500 ms of the most recent such command, the bridge MUST stop the
  motors automatically. The internal "motors live" flag is cleared on the
  cutoff so the timeout does not re-fire every tick.
- The deadman is a fail-safe, not a heartbeat. The controller is still
  responsible for sending `stop` or zero-speed `drive` when it wants the robot
  idle.
- A `stop` command also resets the deadman state.

## Versioning

- Version is reported in the `hello` event (`v` field) and follows
  `MAJOR.MINOR.PATCH`.
- Adding a new event type or a new optional field is a MINOR bump.
- Changing a field's meaning, removing a field, or changing the framing is a
  MAJOR bump.
