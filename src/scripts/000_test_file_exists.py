#!/usr/bin/env python3
# First test - check file existense
from enum import Enum
from db_handling import *
from transports import *

_file_name = 'testfile'
_transport_name = 'SSH'

class Status(Enum):
    COMPLIANT = 1
    NOT_COMPLIANT = 2
    NOT_APPLICABLE = 3
    ERROR = 4
    EXCEPTION = 5

def main():
    try:
        func_status = get_transport(_transport_name).is_exist(_file_name)
    except TransportUnknown:
        return Status.ERROR.value
    if not func_status:
        return Status.NOT_COMPLIANT.value
    if func_status:
        return Status.COMPLIANT.value