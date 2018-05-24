#!/usr/bin/env python3
import pytest

from transports import get_transport


@pytest.fixture
def SNMPconnect():
    return get_transport('SNMP')


@pytest.fixture
def SSHconnect():
    return get_transport('SSH')


def test_get_snmpdata(SNMPconnect):
    assert (str(SNMPconnect.get_snmpdata('.1.3.6.1.2.1.2.2.1.2.1')[0]) ==
            'FastEthernet0/1')


def test_ssh_exec(SSHconnect):
    assert (SSHconnect.exec('uname') == 'Linux')
