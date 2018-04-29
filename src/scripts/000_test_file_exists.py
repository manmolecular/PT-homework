#!/usr/bin/env python3
# First test - check file existense
from db_handling import *
from transports import *

_file_name = 'testfile'
_transport_name = 'SSH'

def main():
    try:
        get_transport(_transport_name).is_exist(_file_name)
    except TransportUnknown:
        return 4
    except TransportIOError:
        return 2
    return 1