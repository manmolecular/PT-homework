# Structure  
## Introduction
Project based on Positive Technologies Python lectures

## Code structure tree
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
|   |   ...
|   │   /* All control-scripts */
|   |   ...
|
└─── templates
│   │   index.html
│   │   style.css
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
- `src/scripts/` - Directory for importing control-libs
- `src/templates/` - Directory for html-pdf templates storing
### Tests  
- `src/tests/` - Pytest tests
### Other tools   
- `img-ubuntu-sshd` - ubuntu sshd dockerfile
- `requirements.txt` - virtualenv python pip requirements
- `docker-compose.yaml` - docker-compose file

# Notes  
## Requirements  
Basically you need just latest python3 (*for example 3.6.5 was used in development of this project*) and pip modules installed from `requirements.txt` file

## Getting start
First you need to build and start docker with ssh and mariadb from root dir of repo:  
```
docker-compose up
```

*Note: to run docker-compose and docker you don't need to use `sudo` - just add your user to `docker` group*
## Connect to SSH
```
ssh root@localhost -p 22022
# password: pwd
```

## Pytest
*Note: run tests from `src/` dir, because modules using relative paths.
From `src/`
```
pytest
```

## PyMySQL + Pytest
To test PyMySQL with pytest you need to install `python3-pymysql` package
```
sudo apt-get install python3-pymysql
```

# Russian README
## Структура репозитория  
- `configs` - конфигурационные *.json* файлы, отвечающие за конфигурацию транспортов по умолчанию в случае использования docker-контейнеров из репозитория (`config.json`) и описание базовых контролей (`controls.json`)
- `controls` - импортируемые в основной модуль скрипты-контроли, отвечающие за основную функциональную составляющую проверок
- `tests` - pytest-тесты для тестирования основного функционала
- `templates` - шаблоны для рендеринга html-страницы и pdf-отчета

## Модули
- `main.py` - основной модуль для запуска тестирования на целевой системе
- `transports.py` - модуль, содержащий в себе классы и основной функционал транспортов. Также содержит в себе классы для обработки исключений.
- `report.py` - модуль, отвечающий за финальную обработку данных и конечную сборку pdf-отчета
- `get_config.py` - модуль, содержащий в себе настройки подключения по умолчанию в рамках данной сборки
- `db_handling.py` - модуль, отвечающий за работу с sqlite базой данных и обработку отчетных данных

## Как работать с проектом
### Зависимости
Для работы с проектом предпочтительно использование `pyenv` с python версии `3.6.5` или новее. Все необходимые pip-зависимости указаны в файле `requirements.txt`, который находится в корне репозитория.  
  
Также для корректной работы тестов необходимо установить пакет `python3-pymysql`:
```
sudo apt-get install python3-pymysql
```

### Сборка
Для начала работы следует собрать и запустить docker-контейнеры из репозитория - для упрощения этого процесса в корневой директории содержится `docker-compose` конфигурационный файл. Для запуска и сборки всех необходимых инструментов, следует запустить из директории с файлом следующую команду:
```
docker-compose up
```

*Замечание: для подъема и сборки docker-контейнера нет необходимости в `sudo` правах - достаточно добавить текущего пользователя в группу `docker` системы*

### Стиль
Формат кода в проекте должен соответствовать PEP8.

### Использование контролей и свох скриптов
Для использования своих тестов достаточно поместить их в директорию `scripts/` с именем в формате:
```
000_some_name.py
```

Где `000` - это id проверки, а `some_name` - произвольное имя проверки. Все функции контроля должны быть вызваны из главной функции `main()`, которая импортируется главным функциональным модулем приложения.
*Замечание: количество цифр в названии не имеет значения - любой другой числовой формат будет распознан. Имя может не содержать в себе `_`, но следование общему формату тестов контролей желательно.*

Также следует добавить `id` и описание проверки `descr` в файл `controls.json`, располагающийся в директории `configs`

### Тестирование
Для запуска тестов следует запустить следующую команду из директории `src/`:
```
pytest
```

*Важно: то, откуда будет запущена команда `pytest`, имеет значение по причине относительных путей в проекте. Поэтому, следует запускать `pytest` из директории `src/`*  
