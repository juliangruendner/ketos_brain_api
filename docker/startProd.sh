#!/bin/bash
pip3 install -r requirements.txt

cd mlService_DockerApi
git pull
python3 ../src/dockerAPI.py