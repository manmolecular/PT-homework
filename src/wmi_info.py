from transports import WMItransport, WMIregistryTransport

def get_wmi_info():
    win7 = WMItransport('172.16.22.11', None, 'administrator', 'P@ssw0rd')
    win12 = WMItransport('172.16.22.10', None, 'administrator', 'P@ssw0rd')

    win7_all = {
        'network_config': str(win7.wmi_query("select IPAddress, MACAddress from \
            Win32_NetworkAdapterConfiguration where ipenabled = true")[0]).split('\n'),
        'vulns': str(win7.wmi_query("select hotfixid from \
            win32_quickfixengineering")[0])
    }
    win12_all = {
        'network_config': str(win12.wmi_query("select IPAddress, MACAddress from \
            Win32_NetworkAdapterConfiguration where ipenabled = true")[0]).split('\n'),
        'vulns': str(win12.wmi_query("select hotfixid from \
            win32_quickfixengineering")[0])
    }

    win7_info = {
        'ip': win7_all['network_config'][4],
        'mac': win7_all['network_config'][5],
        'vulns': win7_all['vulns']
    }
    win12_info = {
        'ip': win7_all['network_config'][4],
        'mac': win12_all['network_config'][5],
        'vulns': win12_all['vulns']
    }

    win_audit = {
        'win7': win7_info,
        'win12': win12_info
    }

    return win_audit