#!/bin/bash
# Build and run ssh docker
set -e

cd ./img-ubuntu-sshd/ && sudo docker build . -t img-ubuntu-sshd
sudo docker run -d -p 22022:22 --name cont-ubuntu-sshd img-ubuntu-sshd
ssh-keygen -f "/home/user/.ssh/known_hosts" -R [localhost]:22022