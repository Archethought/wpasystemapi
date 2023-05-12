#!/usr/bin/env python

import hashlib
import click

def parse_wpa_supplicant_config(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    preamble = {}
    networks = []
    network = None

    for line in lines:
        line = line.strip()

        if line.startswith("network={"):
            if network:
                networks.append(network)
            network = {}
        elif line == "}":
            if network:
                networks.append(network)
                network = None
        else:
            if network is not None:
                key, value = line.split("=", 1)
                network[key.strip()] = value.strip()
            else:
                key, value = line.split("=", 1)
                preamble[key.strip()] = value.strip()

    return preamble, networks

@click.command()
@click.option("--file-path", default="/etc/wpa_supplicant/wpa_supplicant.conf", help="Path to the wpa_supplicant.conf file.")
@click.option("--new-ssid", help="New SSID to be added or updated.")
@click.option("--new-password", help="Password for the new SSID.")
@click.option("--delete-ssid", help="SSID to be removed.")
@click.pass_context
def update_wpa_supplicant_config(ctx, file_path, new_ssid, new_password, delete_ssid):
    if not any([new_ssid, new_password, delete_ssid]):
        ctx.fail("No arguments provided. Use --help to display the available options.")
    
    if delete_ssid:
        remove_ssid(file_path, delete_ssid)
    elif new_ssid and new_password:
        if not (8 <= len(new_password) <= 63):
            print("Error: Password must be between 8 and 63 printable ASCII characters.")
            return

        preamble, networks = parse_wpa_supplicant_config(file_path)

        new_psk = hashlib.pbkdf2_hmac('sha1', new_password.encode(), new_ssid.encode(), 4096, 32).hex()

        ssid_exists = False
        for network in networks:
            if network["ssid"] == f'"{new_ssid}"':
                network["psk"] = new_psk
                ssid_exists = True
                break

        if not ssid_exists:
            new_network = {
                "ssid": f'"{new_ssid}"',
                "psk": new_psk
            }
            networks.append(new_network)

        with open(file_path, 'w') as f:
            for key, value in preamble.items():
                f.write(f"{key}={value}\n")

            for network in networks:
                f.write("network={\n")
                for key, value in network.items():
                    f.write(f"\t{key}={value}\n")
                f.write("}\n")

def remove_ssid(file_path, ssid_to_delete):
    preamble, networks = parse_wpa_supplicant_config(file_path)

    original_count = len(networks)
    networks = [network for network in networks if network["ssid"] != f'"{ssid_to_delete}"']

    if len(networks) == original_count:
        print(f"Error: No matching SSID '{ssid_to_delete}' found to delete.")
        return

    with open(file_path, 'w') as f:
        for key, value in preamble.items():
            f.write(f"{key}={value}\n")

        for network in networks:
            f.write("network={\n")
            for key, value in network.items():
                f.write(f"\t{key}={value}\n")
            f.write("}\n")

if __name__ == "__main__":
    update_wpa_supplicant_config()
