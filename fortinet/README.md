# Fortinet Policy Templates

Policy definitions for Fortinet FortiGate (FortiOS).

## Expected config format

FortiOS CLI configuration as returned by `show full-configuration` (or `show`): `config ...` / `edit ...` / `set ...` / `next` / `end` blocks with indented `set` lines.

## Available Policies

| File | Framework | Purpose | Rules | Minimum rConfig |
|---|---|---|---|---|
| `fortigate_base.policy` | None (build template) | Example baseline build: hostname, timezone, admin access, LAN interface, DHCP, DNS, NAT and firewall policies, SNMP, NTP and logging. Uses fixed example values (for example `set hostname MyFortinet`, 192.168.88.0/24); edit them before use. | 12 | V8.0.0 |
| `fortinet_fortios_base.policy` | None (generic hardening) | rConfig Base Coverage for FortiOS (generic hardening), version 1.0. | 8 | V8.0.2 |
| `fortinet_fortios_CIS_benchmark.policy` | CIS-style | CIS-style Baseline mapped to FortiOS (coverage aligned with IOS CIS), version 1.0. | 8 | V8.0.2 |
| `fortinet_fortios_FORTINETSAFE_benchmark.policy` | Cisco SAFE (adapted) | Cisco SAFE-aligned Baseline adapted for Fortinet FortiOS, version 1.0. | 9 | V8.0.2 |
| `fortinet_fortios_HIPAA_benchmark.policy` | HIPAA | HIPAA Technical Safeguards mapped to FortiOS, version 1.0. | 8 | V8.0.2 |
| `fortinet_fortios_ISO27K_benchmark.policy` | ISO/IEC 27001 / 27002 Annex A | ISO/IEC 27001/27002 Annex A mapped to FortiOS, version 1.0. | 7 | V8.0.2 |
| `fortinet_fortios_NIST_benchmark.policy` | NIST SP 800-53 | NIST SP 800-53 Technical Controls mapped to FortiOS, version 1.0. | 8 | V8.0.2 |
| `fortinet_fortios_NISTCSF_benchmark.policy` | NIST CSF | NIST Cybersecurity Framework mapped to FortiOS, version 1.0. | 8 | V8.0.2 |
| `fortinet_fortios_PCIDSS_benchmark.policy` | PCI DSS | PCI DSS mapped to FortiOS, version 1.0. | 8 | V8.0.2 |

The minimum version comes from the methods each file uses: `must_not_match_regex` needs V8.0.2 or later.

## Supported Models

Not stated by the policy authors.

## Implementation Notes

- Control IDs are rConfig's own numbering. They are not taken from the published benchmark or standard documents.
- `fortigate_base.policy` and `fortinet_fortios_base.policy` are separate files with different purposes: the first is a build template with fixed values, the second checks generic hardening settings.
- `match_code_block_from_array` matches its lines as consecutive lines in the config. Settings that FortiOS prints between them (for example other `set` lines inside `config system global`) cause the rule to fail.
