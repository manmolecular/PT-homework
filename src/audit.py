from transports import get_transport, SNMPtransport
import re

connection = get_transport('SNMP')
sysDescr = connection.get_snmpdata('.1.3.6.1.2.1.1.1.0')
for value in sysDescr:
    print(value)

interfacesQuantity = connection.get_snmpdata('.1.3.6.1.2.1.2.1.0')[0]
listOfInterfaces = []
for interface in range(1, interfacesQuantity):
    listOfInterfaces.append([
        ((connection.get_snmpdata('.1.3.6.1.2.1.2.2.1.2.'+ str(interface))[0]).prettyPrint()),
        (connection.get_snmpdata('.1.3.6.1.2.1.2.2.1.7.'+ str(interface))[0].prettyPrint())
    ])

listOfInterfaces.sort()
for interface in listOfInterfaces:
    print (interface)