#!/bin/bash

python3 -m coverage run -m unittest src/test_app.py
python3 -m coverage html
