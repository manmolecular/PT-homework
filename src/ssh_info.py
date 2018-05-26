from transports import *

ssh_ubuntu = SSHtransport('172.16.22.32', 22, 'scan_user', 'P@ssw0rd')
ssh_centos = SSHtransport('172.16.22.33', 22, 'scan_user', 'P@ssw0rd')

ubuntu_info = {
    'ASLR': ssh_ubuntu.exec('sysctl kernel.randomize_va_space')
    #'SusPackages': []
}

ssh_centos = {
    'ASLR': ssh_centos.exec('sysctl kernel.randomize_va_space')
}

print(ubuntu_info)
print(ssh_centos)