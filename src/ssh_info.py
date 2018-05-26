from transports import SSHtransport

def get_ssh_info():
    ssh_ubuntu = SSHtransport('172.16.22.32', 22, 'scan_user', 'P@ssw0rd')
    ssh_centos = SSHtransport('172.16.22.33', 22, 'scan_user', 'P@ssw0rd')
    ubuntu_info = {
        'ASLR': ssh_ubuntu.exec('sysctl kernel.randomize_va_space'),
        'SusPackages': [ssh_ubuntu.exec('sysctl net.ipv4.conf.all.log_martians'), 
                            ssh_ubuntu.exec('sysctl net.ipv4.conf.default.log_martians')],
        'LoginGraceTime': ssh_ubuntu.exec('grep "^LoginGraceTime" /etc/ssh/sshd_config'),
        'Heartbleed': ssh_ubuntu.exec('dpkg --list | grep OpenSSL')
    }

    centos_info = {
        'ASLR': ssh_centos.exec('/sbin/sysctl kernel.randomize_va_space'),
        'SusPackages': [ssh_centos.exec('/sbin/sysctl net.ipv4.conf.all.log_martians'),
                            ssh_centos.exec('/sbin/sysctl net.ipv4.conf.default.log_martians')],
        'LoginGraceTime': ssh_centos.exec('grep "^LoginGraceTime" /etc/ssh/sshd_config'),
        'Heartbleed': ssh_centos.exec('rpm -qa | grep OpenSSL')
    }

    ssh_audit = {
        'ubuntu': ubuntu_info,
        'centos': centos_info
    }

    return ssh_audit