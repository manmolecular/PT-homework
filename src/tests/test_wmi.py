#!/usr/bin/env python3
import wmi

import pytest

from transports import get_transport


@pytest.fixture
def WMIconnect():
    return get_transport('WMI')

@pytest.fixture
def WMIregistry():
    return get_transport('WMIreg')


def test_valid_command_status(WMIconnect):
    assert (bool(WMIconnect.wmi_exec('ipconfig')['result']) == False)


def test_return_object_wmi_query(WMIconnect):
    result = WMIconnect.wmi_query("Select Name, \
            DNSHostName, Domain, Workgroup, PartOfDomain \
            from Win32_ComputerSystem")[0]
    assert isinstance(result, wmi._wmi_object)


def test_registry_get_value(WMIregistry):
    result = WMIregistry.get_value(
        'Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System',
        'EnableLUA')
    accepted_values = [0, 1]
    assert result in accepted_values
