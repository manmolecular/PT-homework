#!/usr/bin/env python3
from transports import WMIregistryTransport, get_transport, TransportUnknown
from db_handling import Status

TRANSPORT = 'WMIreg'


def main():
    try:
        reg =  get_transport(TRANSPORT)
        result = reg.get_value(
            'Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System',
            'EnableInstallerDetection')
    except TransportUnknown:
        return Status.STATUS_ERROR
    if bool(result):
        return Status.STATUS_COMPLIANT
    else:
        return Status.STATUS_NOT_COMPLIANT