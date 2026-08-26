# NetBox Source-of-Truth to Cisco RESTCONF Automation Pipeline

![Cisco ENCOR Specialist](https://img.shields.io/badge/Cisco-ENCOR_350--401-blue.svg)
![Python 3.10+](https://img.shields.io/badge/Python-3.10+-brightgreen.svg)
![NetDevOps](https://img.shields.io/badge/Architecture-NetDevOps_SoT-orange.svg)

## Overview
This repository contains an enterprise NetDevOps pipeline that extracts dynamic network interface configurations from **NetBox (Source-of-Truth)**, processes raw CIDR/network properties, and programmatically deploys configurations to **Cisco IOS-XE** devices using **RESTCONF (YANG data model)**.

## Key Features
- **NetBox SoT Integration:** Pulls dynamic interface details via JSON REST API parameters.
- **CIDR Subnet Math Processor:** Automates calculation of dotted-decimal netmasks from CIDR strings.
- **RESTCONF / YANG Data Model:** Programmatically updates device state via HTTP PATCH calls.
- **Zero-Dependency Mock Engine:** Features a full test harness for running CI/CD pipelines without external sandbox hardware locks.

## Topology & Workflow
`[ NetBox API ] ──(JSON)──> [ Python Middleware ] ──(RESTCONF Payload)──> [ Cisco Device ]`

## Verified Execution Output

[*] Initializing Network Automation Pipeline [MOCKED ARCHITECTURE]...
[+] Fetching interface data from NetBox Source-of-Truth...
Loaded data for interface: GigabitEthernet2
[+] Rendering RESTCONF JSON payload via Automation Engine...
Rendered Payload Preview:
{
"Cisco-IOS-XE-native:interface": {
"GigabitEthernet": [
{
"name": "GigabitEthernet2",
"description": "Configured via NetBox Source of Truth Automation Pipeline",
"ip": {
"address": {
"primary": {
"address": "192.168.10.1",
"mask": "255.255.255.0"
}
}
},
"shutdown": false
}
]
}
}
[+] Deploying RESTCONF configuration to Cisco target device...

[SUCCESS] Configuration successfully synchronized from NetBox to Cisco Device via RESTCONF!

