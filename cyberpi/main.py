# Entry point uploaded to CyberPi via mBlock 5 Upload Mode.
# Boots the serial bridge; everything else lives in bridge.py.

import cyberpi  # noqa: F401 (provided by CyberPiOS)
import bridge


def _banner():
    try:
        cyberpi.console.println("cyberpi-bridge v" + bridge.FW_VER)
    except Exception:
        pass


_banner()
bridge.run()
