#!/usr/bin/env python3
# First test - check file existense
from db_handling import *
from transports import *

_file_name = 'testfile'
_transport_name = 'SSH'

def main():
    try:
        func_status = get_transport(_transport_name).is_exist(_file_name)
    except TransportUnknown:
        return Status.STATUS_ERROR.value
    if not func_status:
        return Status.STATUS_NOT_COMPLIANT.value
    if func_status:
        return Status.STATUS_COMPLIANT.value