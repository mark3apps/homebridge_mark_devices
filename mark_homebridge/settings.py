import os

_DEBUG: bool = False


def set_debug(debug: bool):
    global _DEBUG
    _DEBUG = debug


def DEBUG():
    return _DEBUG


def path():
    return "/var/lib/homebridge/modules/homebridge_ac"
