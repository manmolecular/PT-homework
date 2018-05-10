#!/usr/bin/env python3
# First test - check file existense
from transports import get_transport, SSHtransport, TransportUnknown
from db_handling import Status

FILE_NAME = 'testfile'
TRANSPORT = 'SSH'

def main():
    try:
        transport_instance = get_transport(TRANSPORT)
        func_status = transport_instance.get_file(FILE_NAME)
    except TransportUnknown:
        return Status.STATUS_ERROR
    if func_status:
        return Status.STATUS_COMPLIANT
    else:
        return Status.STATUS_NOT_COMPLIANT
