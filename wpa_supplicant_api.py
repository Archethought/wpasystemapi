from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import hashlib
from config import Settings

settings = Settings()

app = FastAPI()

class SsidInfo(BaseModel):
    ssid: str
    password: str

def parse_wpa_supplicant_config(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()

    preamble = {}
    networks = []

    current_network = None

    for line in lines:
        line = line.strip()

        if line.startswith("network="):
            if current_network is not None:
                networks.append(current_network)
            current_network = {}
        elif line.startswith("}"):
            if current_network is not None:
                networks.append(current_network)
                current_network = None
        elif "=" in line and current_network is not None:
            key, value = line.split("=", 1)
            current_network[key.strip()] = value.strip()
        elif "=" in line:
            key, value = line.split("=", 1)
            preamble[key.strip()] = value.strip()

    return preamble, networks

def update_wpa_supplicant_config(file_path, new_ssid, new_password, delete_ssid):
    preamble, networks = parse_wpa_supplicant_config(file_path)

    if delete_ssid:
        networks = [network for network in networks if network["ssid"] != f'"{delete_ssid}"']
    elif new_ssid and new_password:
        hashed_password = hashlib.pbkdf2_hmac("sha1", new_password.encode(), new_ssid.encode(), 4096, 32).hex()
        updated = False
        for network in networks:
            if network["ssid"] == f'"{new_ssid}"':
                network["psk"] = hashed_password
                updated = True
        if not updated:
            networks.append({"ssid": f'"{new_ssid}"', "psk": hashed_password})

    with open(file_path, "w") as f:
        for key, value in preamble.items():
            f.write(f"{key}={value}\n")
        for network in networks:
            f.write("network={\n")
            for key, value in network.items():
                f.write(f"\t{key}={value}\n")
            f.write("}\n")

def remove_ssid(file_path, ssid_to_delete):
    update_wpa_supplicant_config(file_path, None, None, ssid_to_delete)

@app.get("/ssids")
def get_ssids(file_path: str = settings.wpa_supplicant_file_path):
    _, networks = parse_wpa_supplicant_config(file_path)
    return [network["ssid"].strip('"') for network in networks]

@app.get("/ssids/{ssid}")
def get_ssid(ssid: str, file_path: str = settings.wpa_supplicant_file_path):
    _, networks = parse_wpa_supplicant_config(file_path)
    for network in networks:
        if network["ssid"] == f'"{ssid}"':
            return network
    raise HTTPException(status_code=404, detail="SSID not found")

@app.post("/ssids")
def create_ssid(ssid_info: SsidInfo, file_path: str = settings.wpa_supplicant_file_path):
    update_wpa_supplicant_config(file_path, ssid_info.ssid, ssid_info.password, None)
    return {"result": "SSID created or updated successfully"}

@app.put("/ssids/{ssid}")
def update_ssid_password(ssid: str, new_password: str, file_path: str = settings.wpa_supplicant_file_path):
    update_wpa_supplicant_config(file_path, ssid, new_password, None)
    return {"result": "SSID password updated successfully"}

@app.delete("/ssids/{ssid}")
def delete_ssid(ssid: str, file_path: str = settings.wpa_supplicant_file_path):
    remove_ssid(file_path, ssid)
    return {"result": "SSID deleted successfully"}
