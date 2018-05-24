from transports import get_transport, SNMPtransport
import re


def SNMP_audit():
    connection = get_transport('SNMP')
    sysDescr = connection.get_snmpdata('.1.3.6.1.2.1.1.1.0')
    interfacesQuantity = connection.get_snmpdata('.1.3.6.1.2.1.2.1.0')[0]
    listOfInterfaces = []
    for interface in range(1, interfacesQuantity):
        listOfInterfaces.append([
            ((connection.get_snmpdata('.1.3.6.1.2.1.2.2.1.2.'+ str(interface))[0]).prettyPrint()),
            (connection.get_snmpdata('.1.3.6.1.2.1.2.2.1.7.'+ str(interface))[0].prettyPrint())
        ])

    listOfInterfaces.sort()

    SNMP_audit_info = {
        'sysDescr': sysDescr[0],
        'listOfInterfaces': listOfInterfaces
    }
    return SNMP_audit_info


def SSH_audit():
    connection = get_transport('SSH')
    SSH_audit_info = {
        'sys_info': connection.exec('uname -a'),
        'cpu_info': connection.exec('lscpu'),
        'kernel_version': connection.exec('cat /proc/version'),
        'sys_users': connection.exec('cat /etc/passwd'),
        'ip_macs': connection.exec('ip l'),
        'packages': connection.exec('apt list --installed')
    }
    return SSH_audit_info


def retrieve_audit_info():
    return [SNMP_audit(), SSH_audit()]