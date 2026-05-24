# Thin wrapper around the mbot2 motor API.
# Accepts left/right percentages in [-100, 100]; clamps; never raises on
# bad input from the wire.

import mbot2  # provided by CyberPiOS / mBot2 firmware

_MIN = -100
_MAX = 100


def _clamp(v):
    try:
        v = int(v)
    except Exception:
        return 0
    if v < _MIN:
        return _MIN
    if v > _MAX:
        return _MAX
    return v


def drive(l, r):
    mbot2.drive_power(_clamp(l), _clamp(r))


def stop():
    mbot2.drive_power(0, 0)
