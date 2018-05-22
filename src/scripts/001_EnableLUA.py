#!/usr/bin/env python3
from db_handling import Status
from transports import get_transport, TransportUnknown, TransportConnectionError

TRANSPORT = 'WMIreg'


def main():
    try:
        reg = get_transport(TRANSPORT)
        result = reg.get_value(
            'Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System',
            'EnableLUA')
    except TransportConnectionError:
        return Status.STATUS_NOT_APPLICABLE
    except TransportUnknown:
        return Status.STATUS_ERROR
    if result == 1:
        return Status.STATUS_COMPLIANT
    else:
        return Status.STATUS_NOT_COMPLIANT
