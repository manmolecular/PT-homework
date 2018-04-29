#!/bin/bash
set -e

sudo docker run -d -p 22022:22 --name cont-ubuntu-sshd img-ubuntu-sshd 