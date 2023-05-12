#!/bin/bash

uvicorn wpa_supplicant_api:app --reload --host 0.0.0.0 --port 8089
