# mBot2 ↔ StackChan serial bridge

A two-robot setup: a Makeblock mBot2 (CyberPi, ESP32) handles motion and
sensors; an M5Stack CoreS3 running StackChan handles voice and face. They talk
over a single 3.3 V UART at 115200 8N1 using newline-delimited JSON. The wire
protocol is the single source of truth — see
[`protocol/PROTOCOL.md`](protocol/PROTOCOL.md).

## Status

| Side    | Path        | Status        |
| ------- | ----------- | ------------- |
| CyberPi | `cyberpi/`  | in progress   |
| CoreS3  | `cores3/`   | not started   |
