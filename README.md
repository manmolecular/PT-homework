# Structure  
## Repo tree  
```
PT-exercises/src
│   __init__.py
│   db_handling.py
│   get_config.py
│   main.py
|   report.py
|   transports.py
|
└─── configs
│   │   config.json
│   │   controls.json
|   |   ...
│   
└─── scripts
|   │   __init__.py
|   │   000_test_file_exists.py
|   |   ...
|
└─── templates
│   │   index.html
│   │   style.css
|   |   test.html
|   |   ...
|
└─── tests
    │   __init__.py
    │   test_sql.py
    |   test_sqlite.py
    |   test_ssh.py
    |   ...
```
## Files  
### Main code  
- `src/db_handling.py` - Manage all sqlite-database work on this module
- `src/get_config.py` - Parsing of json configuration file
- `src/main.py` - Main module
- `src/transports.py` - Transport classes
- `src/report.py` - Making of pdf scanning report
### Dirs  
- `src/configs/` - Json configs file
- `src/scripts/` - Directory for importing libs
### Tests  
- `src/tests/` - Pytest tests
### Other tools  
- `img-ubuntu-python` - docker with ubuntu and python3  
- `img-ubuntu-sshd` - docker with ubuntu and sshd 
- `requirements.txt` - virtualenv python requirements
- `build-ssh.sh` - up docker ssh server
- `mariadb-up.sh` - up mariadb server
# Notes  
## Requirements  
Basically you need just latest python3 (*for example 3.6.5 or whatever you want*) and pip modules installed from `requirements.txt`
## Build containers of ssh
### You can use `build-ssh.sh` or do it manually:
For python:  
```
cd ./img-ubuntu-python/ && docker build . -t img-ubuntu-python
```
For sshd:
```
cd ./img-ubuntu-sshd/ && docker build . -t img-ubuntu-sshd
```
## Run & connect SSH  
Run:
```
docker run -d -p 22022:22 --name cont-ubuntu-sshd img-ubuntu-sshd 
# password: pwd (change it if you want)
```
Or you can use `server-up.sh` script, which is more faster way
Connect:
```
ssh root@localhost -p 22022
# password: pwd
```
## Paramiko  
```
sudo pip3 install paramiko
```
## Pytest
From `src/tests/`
```
pytest
```
## PyMySQL + Pytest
To test PyMySQL with pytest you need to install `python3-pymysql` package
```
sudo apt-get install python3-pymysql
```
