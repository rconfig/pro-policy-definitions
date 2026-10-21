# Juniper Policy Templates

Policy definitions for Juniper Junos devices.

> [!WARNING]
> These rules have not yet been checked against a real Junos device. Their status is `synthetic-tested`: the expected results are recorded against synthetic `display set` samples built from rConfig Pro's demo generator and Junos command syntax. Check the results on one of your own devices before you rely on them.

## Expected config format

Junos set format, as returned by `show configuration | display set`, with one `set` command per line:

```
set system services ssh protocol-version v2
set system syslog host 192.0.2.50 any notice
```

This is the command rConfig's Junos demo platform collects. The rules do not match brace (hierarchical) format from `show configuration`.

## Available Policies

| File | Purpose | Rules | Minimum rConfig |
|---|---|---|---|
| `junos-management-access.policy` | SSH enabled without protocol version 1, SSH cipher and MAC lists with no CBC, 3DES, arcfour, blowfish, MD5, SHA-1 or RIPEMD-160 algorithm, no Telnet, a login banner, and a login class idle-timeout of 1 to 10 minutes. | 5 | V8.3.0 |
| `junos-aaa.policy` | An authentication order that starts with RADIUS or TACACS+ and ends with local password fallback, and no MD5 (`$1$`) password hash for root or any local user. | 2 | V8.0.2 |
| `junos-snmp.policy` | No SNMPv1 or SNMPv2c communities, and SNMPv3 USM users with SHA authentication and AES-128 privacy and none with MD5, DES, 3DES or none. | 2 | V8.3.0 |
| `junos-logging.policy` | A remote syslog host for any facility at info or notice, and for authorization messages at info; millisecond timestamps; no console logging; and the UTC time zone. | 5 | V8.0.2 |
| `junos-services.policy` | No finger, FTP, rlogin, rsh or rexec service, and ICMP redirects disabled (`set system no-redirects`). | 2 | V8.0.2 |
| `junos-interfaces.policy` | Every interface is disabled or has a description. | 1 | V8.0.2 |

The minimum version comes from the methods each file uses: `must_not_match_regex` needs V8.0.2 or later and `evaluate_block` needs V8.3.0 or later. Earlier releases skip the rules they do not support.

Each file's `.meta.yaml` lists the published references for each rule, where one exists: the NIST SP 800-53 control, the HIPAA 45 CFR section and the NIST CSF 1.1 subcategory.

## Supported Models

Not stated by the policy authors. The rules use generic Junos `[edit system]`, `[edit snmp]` and `[edit interfaces]` syntax.

## Implementation Notes

- Junos does not print a setting that is at its default. SSH protocol version 2 and the UTC time zone are the defaults, so those rules fail only when a different value is set (`protocol-version` with `v1`, or a `set system time-zone` line other than `UTC`). ICMP redirects are sent by default, so `set system no-redirects` must be present.
- Multi-value settings are matched in the bracket form, for example `set system authentication-order [ tacplus password ]`. The SSH cipher and MAC rule also accepts one value per line.
- `plain-text-password` is never stored: Junos keeps only the `encrypted-password` hash. The AAA rule therefore checks the hash type and fails on an MD5 (`$1$`) hash.
- The interface rule expects each interface's `set interfaces <name> ...` lines to be next to each other, as `display set` prints them. A description on a unit (`set interfaces irb unit 99 description ...`) does not count; set it on the interface. `interface-range` entries are not checked.
- The idle-timeout rule needs at least one login class with an idle-timeout. The built-in classes such as `super-user` cannot carry one, so users in those classes are not covered.
- A deactivated statement still appears in `display set` output as a `set` line followed by a `deactivate` line, and the rules treat it as configured.
- Regex rules use the `/.../m` form so that `^` and `$` match at each line of the config.
