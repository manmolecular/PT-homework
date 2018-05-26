from netmiko import ConnectHandler
import re

pattern_v = 'ssh version \d'
pattern_t = 'ssh timeout \d'
ips = ['172.16.22.2', '172.16.22.3', '172.16.22.4', '172.16.22.5']

class SSHmikotransport():
    def __init__(self, device, host, login, password):
        self.client = None
        try:
            self.client = ConnectHandler(
                device_type=device,
                ip=host,
                username=login,
                password=password)
        except Exception as e:
            raise e
        
    def enable(self):
        self.client.enable()
    
    def exec(self, command):
        if not command:
            raise TransportError({'command': command})
        data = self.client.send_command(command)
        return data
    
    def __del__(self):
        self.client.disconnect()

def get_netmiko(device='cisco_asa',host = '172.16.22.2',login='admin',pwd='P@ssw0rd'):
    return SSHmikotransport(device = device, host = host, login = login, password=pwd)

def check_ssh_version_1():
    true_version = 2
    client = get_netmiko(host = '172.16.22.2')
    client.exec('terminal pager 0')
    data = client.exec('show running-config')
    if int(re.search(pattern_v,data).group(0).split()[2]) == true_version: return True
    return False
            
def check_ssh_version_2():
    true_version = 2
    client = get_netmiko(host = '172.16.22.3')
    client.enable()
    client.exec('terminal pager 0')
    data = client.exec('show running-config')
    #print(data)
    try:
        if int(re.search(pattern_v,data).group(0).split()[2]) == true_version: return True
    except:
        return False
    return False

def check_ssh_version_3():
    true_version = 2
    client = get_netmiko(device = 'cisco_csr', host = '172.16.22.4')
    client.enable()
    client.exec('terminal pager 0')
    data = client.exec('show running-config')
    #print(data)
    try:
        if int(re.search(pattern_v,data).group(0).split()[2]) == true_version: return True
    except:
        return False
    return False

def check_ssh_timeout_1():
    true_timeout = 10
    client = get_netmiko(host = '172.16.22.2')
    client.exec('terminal pager 0')
    data = client.exec('show running-config')
    if int(re.search(pattern_t,data).group(0).split()[2]) < true_timeout: return True
    return False

def check_ssh_timeout_2():
    true_version = 10
    client = get_netmiko(host = '172.16.22.3')
    client.enable()
    client.exec('terminal pager 0')
    data = client.exec('show running-config')
    if int(re.search(pattern_t,data).group(0).split()[2]) < true_version: return True
    return False

def get_cisco_info():
    cisco_info = {
    'AccessRulesFor_1_Stand': check_ssh_version_1(),
    'AccessRulesFor_2_Stand': check_ssh_version_2(),
    'AccessRulesFor_3_Stand': 'We were out of time',
    'AccessRulesFor_4_Stand': 'We were out of time',
    'CheckSSHTimeOutFor_1_Stand': check_ssh_timeout_1(),
    'CheckSSHTimeOutFor_2_Stand': check_ssh_timeout_2(),
    'CheckSSHTimeOutFor_3_Stand': 'We were out of time',
    'CheckSSHTimeOutFor_4_Stand': 'We were out of time'}
    return cisco_info