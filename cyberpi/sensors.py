# Sensor reads. Each function returns `None` on failure rather than raising,
# so the bridge can silently skip a tick.

try:
    import mbuild  # mBuild bus, where Ultrasonic Sensor 2 lives
except Exception:
    mbuild = None


# Daisy-chain index of the ultrasonic on the mBuild bus. Adjust if you have
# more than one module on the chain.
_US_INDEX = 1


def read_distance_cm():
    if mbuild is None:
        return None
    try:
        v = mbuild.ultrasonic2.get(index=_US_INDEX)
    except Exception:
        return None
    if v is None:
        return None
    try:
        cm = float(v)
    except Exception:
        return None
    # The sensor reports a sentinel (often a very large value or negative) on
    # out-of-range reads. Treat those as failures.
    if cm < 0 or cm > 400:
        return None
    return cm
