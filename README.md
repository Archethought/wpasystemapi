# Raspberry Pi WiFi management using FastAPI
## Description
An open source system for managing WiFi file wpa_supplicant.conf on the Raspberry Pi.

WARNING: This repo is for education and does not comprehend security practices around
a file you really need to protect. Haven't gotten there yet. Feel free to contribute.

*You've been warned.*

## Why do this?
There were two goals:
1. Learn more about FastAPI
1. Hating to modify the wpa_supplicant.conf file by hand
1. Get better at detecting "off by one" errors

## Setup and prerequisites
Current Raspberry Pi as of this writing is Bullseye.

```
python3 -m venv venv3
. ./venv3/bin/activate
pip install -U pip
pip install wheel
pip install -r requirements.txt
```

## Usage
There is a run-wpa.sh shell script containing the run command for `uvicorn`

```
uvicorn wpa_supplicant_api:app --reload --host 0.0.0.0 --port 8089
```
*N.B. 0.0.0.0 opens the API to all outside of the host.*

There is a command line version of the program. To get help for it
```
python wpa_update_cli.py
```

## Settings
The file `config.py` contains the class `Settings` for
* File path location for `wpa_supplicant.conf`
* Environment variable prefix
* The .env file if it exists

N.B. the file /etc/wpa_supplicant/wpa_supplicant.conf is root access only. Take this into account.

## Future
The Raspberry Pi OS may switch to a different WiFi management methodology at any time.

## License
Released under MIT License  

Copyright (c) 2023 Archethought Inc.  
