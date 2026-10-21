# Fortinet Policy Templates

Policy definitions for Fortinet FortiGate (FortiOS).

## Expected config format

FortiOS CLI configuration as returned by `show full-configuration` (or `show`): `config ...` / `edit ...` / `set ...` / `next` / `end` blocks with indented `set` lines.

## Available Policies

| File | Purpose | Rules | Minimum rConfig |
|---|---|---|---|
| `fortios-build-template.policy` | Starting template for a new build, not a compliance check. Example values for hostname, timezone, admin access, LAN interface, DHCP, DNS, NAT and firewall policies, NTP and logging (for example `set hostname MyFortinet`, 192.168.88.0/24). Replace them with your own before use. | 10 | V8.0.0 |
| `fortios-management-access.policy` | Admin HTTPS with strong crypto and no admin HTTP, a 10-minute admin idle timeout, login banner and MOTD, no insecure protocols in interface `allowaccess`, and an admin address group. | 5 | V8.3.0 |
| `fortios-aaa.policy` | A RADIUS server with an address, and an enabled password policy with a minimum length of 12. | 2 | V8.3.0 |
| `fortios-snmp.policy` | No SNMPv1 or SNMPv2c communities, and SHA authentication with AES privacy for every SNMPv3 user. | 2 | V8.3.0 |
| `fortios-logging.policy` | Remote syslog enabled with a server on UDP port 514, and a syslog filter severity of information or notice. | 2 | V8.3.0 |

The minimum version comes from the methods each file uses: `evaluate_block` needs V8.3.0 or later. Earlier releases skip the rules they do not support.

Each topic file's `.meta.yaml` lists the published references for each rule, where one exists: the NIST SP 800-53 control, the HIPAA 45 CFR section and the NIST CSF 1.1 subcategory.

## Supported Models

Not stated by the policy authors.

## Implementation Notes

- Rules on a `config ...` section use `evaluate_block` with a `scope:` such as `^config system global$`. The `set` lines can appear in any order inside the section, and other `set` lines between them do not matter.
- `equals:` compares the whole trimmed line, so `set admintimeout 10` does not match `set admintimeout 100`.
- A scoped rule fails when no config section matches its scope. A config with no `config user radius` section therefore fails the RADIUS rule.
- The password rule accepts `set min-length 12` (older FortiOS) or `set minimum-length 12` (FortiOS 7).
- The SNMPv3 rule checks the whole `config system snmp user` section, so one user with a non-SHA `auth-proto` or a non-AES `priv-proto` fails it.
