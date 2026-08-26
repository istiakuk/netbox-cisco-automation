import json
import argparse
import requests
from unittest.mock import Mock

def calculate_netmask(cidr_str):
    """Convert CIDR notation (e.g., /24) to subnet mask string."""
    ip, cidr = cidr_str.split('/')
    cidr = int(cidr)
    mask = (0xffffffff >> (32 - cidr)) << (32 - cidr)
    netmask = f"{(mask >> 24) & 0xff}.{(mask >> 16) & 0xff}.{(mask >> 8) & 0xff}.{mask & 0xff}"
    return ip, netmask

def fetch_netbox_data(mock_mode=True):
    """Retrieve interface specifications from Source of Truth."""
    if mock_mode:
        with open("mock_data/netbox_device.json", "r") as f:
            return json.load(f)
    else:
        headers = {
            "Authorization": "Token YOUR_NETBOX_API_TOKEN",
            "Accept": "application/json"
        }
        response = requests.get("https://netbox.local/api/dcim/interfaces/", headers=headers, verify=False)
        return response.json()

def render_restconf_payload(netbox_data):
    """Parse NetBox JSON and construct RESTCONF JSON payload directly."""
    device_data = netbox_data["results"][0]
    raw_ip = device_data["ip_addresses"][0]["address"]
    ip_addr, netmask = calculate_netmask(raw_ip)

    # Build structured RESTCONF YANG data dictionary directly to guarantee valid JSON booleans
    payload = {
        "Cisco-IOS-XE-native:interface": {
            "GigabitEthernet": [
                {
                    "name": device_data["name"],
                    "description": device_data["description"],
                    "ip": {
                        "address": {
                            "primary": {
                                "address": ip_addr,
                                "mask": netmask
                            }
                        }
                    },
                    "shutdown": not device_data["enabled"]
                }
            ]
        }
    }
    return payload

def push_restconf_config(payload, mock_mode=True):
    """Push configured payload via RESTCONF HTTP PATCH to target device."""
    url = "https://sandbox-iosxe.cisco.com:9443/restconf/data/Cisco-IOS-XE-native:native/interface"
    headers = {
        "Content-Type": "application/yang-data+json",
        "Accept": "application/yang-data+json"
    }

    if mock_mode:
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.text = ""
        response = mock_response
    else:
        response = requests.patch(url, headers=headers, auth=("developer", "C1sco12345"), json=payload, verify=False)

    return response

def main():
    parser = argparse.ArgumentParser(description="NetBox to Cisco RESTCONF Automation Engine")
    parser.add_argument("--live", action="store_true", help="Run against live endpoints instead of mocked environment")
    args = parser.parse_args()

    use_mock = not args.live
    mode_label = "MOCKED ARCHITECTURE" if use_mock else "LIVE NETWORK"

    print(f"[*] Initializing Network Automation Pipeline [{mode_label}]...")

    print("[+] Fetching interface data from NetBox Source-of-Truth...")
    sot_data = fetch_netbox_data(mock_mode=use_mock)
    print(f"    Loaded data for interface: {sot_data['results'][0]['name']}")

    print("[+] Rendering RESTCONF JSON payload via Automation Engine...")
    payload = render_restconf_payload(sot_data)
    print("    Rendered Payload Preview:")
    print(json.dumps(payload, indent=2))

    print("[+] Deploying RESTCONF configuration to Cisco target device...")
    res = push_restconf_config(payload, mock_mode=use_mock)

    if res.status_code in [200, 201, 204]:
        print("\n[SUCCESS] Configuration successfully synchronized from NetBox to Cisco Device via RESTCONF!")
    else:
        print(f"\n[ERROR] Deployment failed with HTTP Status Code: {res.status_code}")

if __name__ == "__main__":
    main()
