#!/usr/bin/bash

mkdir data
mkdir reports
mkdir err_msg
touch private_data.json
touch chat_ids.txt

python3 -m venv venv
source venv/bin/activate

pip install -U pip
pip install wheel
pip install -r requirements.txt

