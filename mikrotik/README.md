# MikroTik Policy Templates

Policy definitions for MikroTik RouterOS.

## Expected config format

RouterOS configuration as returned by `/export`, with one command per line.

## Available Policies

| File | Purpose | Rules | Minimum rConfig |
|---|---|---|---|
| `mikrotik_base.policy` | Example baseline build: identity, timezone, secure access and service lockdown, LAN bridge, DHCP, DNS, NAT, firewall filter, SNMP, NTP and remote logging. Uses fixed example values (for example 192.168.88.0/24, `Europe/Dublin`); edit them before use. | 12 | V8.0.0 |

All methods used are available in every V8 release.

## Supported Models

Not stated by the policy authors.

## Implementation Notes

- Several lines are commands rather than exported configuration (for example `/system reset-configuration ...` and `/user add ... password=...`). `/export` output never contains them, so those rules cannot pass against a collected config.
