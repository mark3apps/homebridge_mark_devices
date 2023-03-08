_DEBUG: bool = False

BASE_PATH = (
    "/var/lib/homebridge/modules/homebridge_mark_devices/homebridge_mark_devices"
)


def set_debug(debug: bool):
    global _DEBUG
    _DEBUG = debug


def DEBUG():
    return _DEBUG
