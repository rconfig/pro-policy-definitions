# Cisco Policy Templates

Policy definitions for Cisco IOS and IOS XE devices.

## Expected config format

Running configuration as returned by `show running-config`. Top-level commands start in column 0 and interface or line sub-commands are indented, as on the device.

## Available Policies

| File | Framework | Purpose | Rules | Minimum rConfig |
|---|---|---|---|---|
| `cisco_ios_base.policy` | None (build template) | Example baseline build: hostname, timezone, secure access, LAN interface, DHCP, DNS, NAT, ACL, SNMP, NTP and logging. Uses fixed example values (for example `hostname MyCiscoRouter`, 192.168.88.0/24); edit them before use. | 12 | V8.0.0 |
| `cisco_ios_CIS_benchmark.policy` | CIS-style | CIS Cisco IOS Benchmark Policy, version 1.0. Sections: 1 Initial Setup, 2 Banner and Identification, 3 Authentication and Access, 4 SNMP, 5 Logging and Auditing, 6 Services and Protocols, 7 Interfaces, 8 Routing, 9 Miscellaneous. | 38 | V8.0.2 |
| `cisco_ios_CISCOSAFE_benchmark.policy` | Cisco SAFE | Cisco SAFE Baseline Policy for Cisco IOS, version 1.0. Sections: IA Identity and Access, VL Visibility and Logging, TD Threat Defense. | 12 | V8.0.0 |
| `cisco_ios_CISCOSBG_benchmark.policy` | Cisco Security Baseline Guides | Cisco Security Baseline Guides Policy for IOS, version 1.0. Sections: MP Management Plane, LOG Logging, IS Insecure Services. | 11 | V8.0.0 |
| `cisco_ios_HIPAA_benchmark.policy` | HIPAA | HIPAA Cisco IOS Policy, version 1.0. Sections: AC Access Control (164.312(a)(1)), AU Audit Controls (164.312(b)), IN Integrity (164.312(c)(1)), TS Transmission Security (164.312(e)(1)). | 13 | V8.0.0 |
| `cisco_ios_ISO27K_benchmark.policy` | ISO/IEC 27001 / 27002 Annex A | ISO/IEC 27001 / 27002 Annex A Policy for Cisco IOS, version 1.0. Sections: A.9 Access Control, A.12 Operations Security, A.13 Communications Security. | 12 | V8.0.0 |
| `cisco_ios_NIST_benchmark.policy` | NIST SP 800-53 | NIST 800-53 Cisco IOS Benchmark Policy, version 1.0. Sections: AC Access Control, IA Identification and Authentication, AU Audit and Accountability, CM Configuration Management, SC System and Communications Protection, SI System Integrity. | 28 | V8.0.2 |
| `cisco_ios_NISTCSF_benchmark.policy` | NIST CSF | NIST CSF Cisco IOS Policy, version 1.0. Sections: ID.AM Asset Management, PR.AC Access Control, PR.PT Protective Technology, DE.CM Security Continuous Monitoring. | 10 | V8.0.2 |
| `cisco_ios_PCIDSS_benchmark.policy` | PCI DSS | PCI DSS Cisco IOS Policy, version 1.0. Sections: Req. 2 Secure Configurations, Req. 6 Access Control, Req. 10 Logging and Monitoring. | 10 | V8.0.2 |

The minimum version comes from the methods each file uses: `must_not_match_regex` needs V8.0.2 or later. All other methods used here are available in every V8 release.

## Supported Models

Not stated by the policy authors. The rules use generic IOS and IOS XE command syntax.

## Implementation Notes

- Control IDs (for example `CIS-1.1.1`, `NIST-AC-2.1`) are rConfig's own numbering. They are not taken from the published benchmark or standard documents.
- Regex rules use the `/.../m` form so that `^` and `$` match at each line of the config.
- `must_not_match_single_string` compares whole lines. For example, `transport input telnet` does not catch `transport input telnet ssh`.
