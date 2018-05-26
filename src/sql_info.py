from transports import MySQLtransport
from transports import SSHtransport

def get_db(host = '172.16.22.29', port = 3306, login = 'sa', pswd = 'sa', database = 'mysql'):
    return MySQLtransport(host, port, login, pswd, database)

def get_ssh(host = '172.16.22.29', port = 22, login = 'scan_user', pswd = 'P@ssw0rd'):
    return SSHtransport(host, port ,login , pswd)

def take_datadir_path():
    return get_db(database = 'information_schema').sql_exec("SELECT variable_value FROM global_variables WHERE variable_name = 'datadir';")[0].pop('variable_value')
    
def check_chmod_dir(path):
    return get_ssh().exec("stat -c %a {}".format(path))

def first():
    path = take_datadir_path()
    if check_chmod_dir(path) == '700': return True
    return False

def take_list():
    return get_db(database = 'mysql').sql_exec("SELECT User,Password FROM user;")

def second():
    users_list = take_list()
    for user in users_list:
        if user['User'] == user['Password']: return False
    return True

def take_priv():
    return get_db(database = 'mysql').sql_exec("SELECT * FROM tables_priv;") 

def third():
    priv_list = take_priv()
    for user in priv_list:
        if user['User'] is not 'admin' and user['Table_priv'] == 'Select': return False
    return True    

def get_sql_info():
    sql_info = {
    'CheckDirectoryChmod'    : first(),
    'CheckLoginPasswordEquality': second(),
    'CheckAdminAccesToTable'       : third()
    }
    return sql_info