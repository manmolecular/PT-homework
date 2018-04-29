# Structure  
## Repo tree  
```
PT-exercises/src
│   __init__.py
│   db_handling.py
│   get_config.py
│   main.py
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
└─── tests
    │   __init__.py
    │   test.py
    |   ...
```
## Files  
### Main code  
- `src/db_handling.py` - *Manage all database work on this module (include json parsing)*
- `src/get_config.py` - *Parsing of json configuration file*
- `src/main.py` - *Main module*
- `src/transports.py` - *SSH transport class*
- `src/requirements.txt` - *virtualenv python requirements*
### Dirs  
- `src/configs/` - *Json configs files*
- `src/scripts/` - *Directory for importing libs*
### Tests  
- `src/tests/` - *Pytest tests*
### Other tools  
- `img-ubuntu-python` - docker with ubuntu and python3  
- `img-ubuntu-sshd` - docker with ubuntu and sshd 
# Notes  
## Build containers  
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
```
pytest main-project/unit_test.py
```
