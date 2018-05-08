#!/usr/bin/env python3
# First test - check file existense
from transports import get_transport, SSHtransport, TransportUnknown, TransportIOError
from db_handling import Status

FILE_NAME = 'unknown'
TRANSPORT = 'SSH'
INFO_COL = []

def main():
    try:
        transport_instance = get_transport(TRANSPORT)
        func_status = transport_instance.get_file(FILE_NAME)
        transport_name = transport_instance.__class__.__name__
        INFO_COL.append(transport_name)
    except TransportUnknown:
        return [TRANSPORT, Status.STATUS_ERROR]
    except TransportIOError:
        return [TRANSPORT, Status.STATUS_EXCEPTION]
    if func_status:
        INFO_COL.append(Status.STATUS_COMPLIANT)
    else:
        INFO_COL.append(Status.STATUS_NOT_COMPLIANT)
    return INFO_COL
