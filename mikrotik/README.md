# MikroTik Policy Templates

Policy definitions for MikroTik RouterOS.

## Expected config format

RouterOS configuration as returned by `/export`, with one command per line.

## Available Policies

| File | Purpose | Rules | Minimum rConfig |
|---|---|---|---|
| `routeros-build-template.policy` | Starting template for a new build, not a compliance check. Example values for identity, timezone, service lockdown, LAN bridge, DHCP, DNS, NAT, firewall filter, NTP and remote logging (for example 192.168.88.0/24, `Europe/Dublin`). Replace them with your own before use. | 10 | V8.3.0 |

The rules use the `evaluate_block` method, which needs rConfig V8.3.0 or later. Earlier releases skip them.

## Supported Models

Not stated by the policy authors.

## Implementation Notes

- Each rule is an `evaluate_block` with one `regex:` per exported line. A line matches when it sits under its section line (for example `/ip service`) and has the given arguments in any order, with other arguments allowed between them. Long lines that `/export` wraps with ` \` are matched across the break.
- To edit a value, change it inside the regex and keep the escaping: `/` is written `\/` and `.` is written `\.`, for example `time-zone-name=Europe\/Dublin`.
- The two catch-all drop rules (`add action=drop chain=input` and `add action=drop chain=forward`) must match the whole line, so they are not satisfied by a drop rule that has other arguments.
- The NTP rule accepts the RouterOS 6 form (`set enabled=yes primary-ntp=... secondary-ntp=...`) or the RouterOS 7 form (`set enabled=yes` under `/system ntp client`, then one `add address=...` per server under `/system ntp client servers`).
