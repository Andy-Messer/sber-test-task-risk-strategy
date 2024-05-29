#!/bin/bash
echo "Installing..."
python3 -m venv env
source ./env/bin/activate
pip install -r requirements.txt
echo "Installation completed!"
