#!/usr/bin/env python3
# First test - check file existense
from db_handling import Status
from transports import get_transport, TransportUnknown, \
TransportConnectionError, TransportIOError

FILE_NAME = 'testfile'
TRANSPORT = 'SSH'


def main():
    try:
        transport_instance = get_transport(TRANSPORT)
        func_status = transport_instance.get_file(FILE_NAME)
    except TransportConnectionError:
        print('Warning: Can not connect to SSH')
        return Status.STATUS_NOT_APPLICABLE
    except TransportUnknown:
        return Status.STATUS_ERROR
    except TransportIOError:
        return Status.STATUS_NOT_COMPLIANT
    if func_status:
        return Status.STATUS_COMPLIANT
    else:
        return Status.STATUS_NOT_COMPLIANT
