#!/usr/bin/env python3
# First test - check file existense
from transports import get_transport, SSHtransport, TransportUnknown
from db_handling import Status

_file_name = 'testfile'
_transport_name = 'SSH'

def main():
    try:
        func_status = get_transport(_transport_name).get_file(_file_name)
    except TransportUnknown:
        return Status.STATUS_ERROR
    if func_status:
        return Status.STATUS_COMPLIANT
    else:
        return Status.STATUS_NOT_COMPLIANT