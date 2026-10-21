# Fortinet Policy Templates

Policy definitions for Fortinet FortiGate (FortiOS).

## Expected config format

FortiOS CLI configuration as returned by `show full-configuration` (or `show`): `config ...` / `edit ...` / `set ...` / `next` / `end` blocks with indented `set` lines.

## Available Policies

| File | Purpose | Rules | Minimum rConfig |
|---|---|---|---|
| `fortios-build-template.policy` | Starting template for a new build, not a compliance check. Example values for hostname, timezone, admin access, LAN interface, DHCP, DNS, NAT and firewall policies, NTP and logging (for example `set hostname MyFortinet`, 192.168.88.0/24). Replace them with your own before use. | 10 | V8.0.0 |
| `fortios-operational-standards.policy` | Drift from your own operational standard, not a hardening check. Example values for NTP servers (192.0.2.10 and 192.0.2.11), syslog servers (192.0.2.20 in `syslogd`, 192.0.2.21 in `syslogd2`), DNS servers (192.0.2.30 and 192.0.2.31) and a hostname pattern (`[a-z]{3}-fw[0-9]{2}`, for example `dub-fw01`), plus a pre-login banner, a description on every interface that is not set to status down, and an SNMP location. Replace the example values with your own before use. | 7 | V8.3.0 |
| `fortios-management-access.policy` | A 10-minute admin idle timeout, no insecure protocols in interface `allowaccess`, strong crypto (`set strong-crypto enable`) and the pre-login banner (`set pre-login-banner enable`). | 4 | V8.3.0 |
| `fortios-aaa.policy` | A RADIUS server with an address, and an enabled password policy with a minimum length of 12. | 2 | V8.3.0 |
| `fortios-snmp.policy` | No SNMPv1 or SNMPv2c communities, and SHA authentication with AES privacy for every SNMPv3 user. | 2 | V8.3.0 |
| `fortios-logging.policy` | Remote syslog enabled with a server on UDP port 514, and a syslog filter severity of information or notice. | 2 | V8.3.0 |

The minimum version comes from the methods each file uses: `evaluate_block` needs V8.3.0 or later. Earlier releases skip the rules they do not support.

Each topic file's `.meta.yaml` lists the references for each rule, where one exists: the NIST SP 800-53 control, the HIPAA 45 CFR section, the NIST CSF 1.1 subcategory and the ISO/IEC 27001:2022 Annex A control.

## Framework files

Generated from the hardening topic files by `.tooling/scripts/generate_frameworks.py`. Do not edit them: change the topic file or its references and run the generator. Each rule is copied unchanged from its topic file, with its control reference at the start of the description.

| File | Contents | Rules | Minimum rConfig |
|---|---|---|---|
| `fortios-nist-800-53.policy` | Every topic rule that lists one or more NIST SP 800-53 controls. | 8 | V8.3.0 |
| `fortios-nist-csf.policy` | Every topic rule that lists one or more NIST CSF 1.1 subcategories. | 2 | V8.3.0 |
| `fortios-hipaa.policy` | Every topic rule that lists one or more HIPAA 45 CFR 164.312 sections. | 7 | V8.3.0 |
| `fortios-iso27001.policy` | Every topic rule that lists one or more ISO/IEC 27001:2022 Annex A controls. | 10 | V8.3.0 |

A framework file lists checks relevant to that framework. It is not a certification or a full assessment.

## Supported Models

Not stated by the policy authors.

## Implementation Notes

- Rules use only settings documented under `config system global` in the [FortiOS 7.4.4 CLI Reference](https://docs.fortinet.com/document/fortigate/7.4.4/cli-reference/1620/config-system-global). `set admin-http`, `set admin-https`, `set motd` and `set admin-addrgrp` are not documented there, so no rule checks them.
- Rules on a `config ...` section use `evaluate_block` with a `scope:` such as `^config system global$`. The `set` lines can appear in any order inside the section, and other `set` lines between them do not matter.
- `equals:` compares the whole trimmed line, so `set admintimeout 10` does not match `set admintimeout 100`.
- A scoped rule fails when no config section matches its scope. A config with no `config user radius` section therefore fails the RADIUS rule.
- The password rule accepts `set min-length 12` (older FortiOS) or `set minimum-length 12` (FortiOS 7).
- The operational standards interface rule checks every `edit` entry in `config system interface`. It expects FortiOS's four-space indentation and counts `set description`, not `set alias`. An empty `set description ""` does not count.
- The operational standards NTP, syslog and DNS rules check that each standard server is configured, not that no other server is. In the syslog rule, escape the dots when you replace an address, for example `192\.0\.2\.20`.
- The SNMPv3 rule checks the whole `config system snmp user` section, so one user with a non-SHA `auth-proto` or a non-AES `priv-proto` fails it.
