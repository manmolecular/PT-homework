#!/bin/bash
# Run mariadb
set -e

docker pull mariadb
docker run --name pt-mariadb -p 127.0.0.1:43306:3306 -e MYSQL_ROOT_PASSWORD=password -e MYSQL_USER=user -e MYSQL_PASSWORD=password -e MYSQL_DATABASE=def_database --rm mariadb:latest