#!/bin/bash

python3 -m venv env
source ./env/bin/activate
pip install -r requirements.txt

python3 -m coverage run -m unittest src/test_app.py
python3 -m coverage html
