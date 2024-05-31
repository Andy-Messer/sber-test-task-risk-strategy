#!/bin/bash

python3 -m coverage run -m unittest tests.py
python3 -m coverage html
