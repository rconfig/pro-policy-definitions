# IP Infusion Policy Templates

Policy definitions for IP Infusion OcNOS.

> [!NOTE]
> These rules are `lab-tested`: the expected results are recorded against a sanitised `show running-config` from a real OcNOS-SP 7.0.0 router (a UfiSpace S9510-28DC-B in the IP Infusion EMEA lab, collected by rConfig), and against a copy of it edited by hand to pass every rule. The OcNOS-DC edition has not been tested. The hand-edited lines use command forms from the IP Infusion command references; where they would print on a real router is a guess.

## Expected config format

Running configuration as returned by `show running-config`. Top-level commands start in column 0, sub-commands are indented one space, and blocks are separated by `!` lines. Many lines end with `vrf management`:

```
feature ssh vrf management
snmp-server enable snmp vrf management
feature ntp vrf management
feature rsyslog
logging remote server 192.0.2.20 5 port 1514 vrf management
!
interface xe16
 description To R6
 ip address 192.0.2.66/31
!
```

This is the retrieval command the rConfig IP Infusion connection templates name. rConfig Pro has no OcNOS demo platform.

## Available Policies

| File | Purpose | Rules | Minimum rConfig |
|---|---|---|---|
| `ocnos-operational-standards.policy` | Drift from your own operational standard, not a hardening check. Example values for NTP servers (192.0.2.10 and 192.0.2.11), remote syslog servers (192.0.2.20 and 192.0.2.21) and a hostname pattern (`[a-z]{3}-(rtr\|sw)[0-9]{2}`, for example `dub-rtr01`), plus an SNMP location. Replace the example values with your own before use. | 4 | V8.3.0 |
| `ocnos-management-access.policy` | No Telnet (`feature telnet`), SSH enabled on the management VRF (`feature ssh vrf management`), and a custom login banner (`banner motd`, other than `banner motd default`). | 3 | V8.0.2 |
| `ocnos-aaa.policy` | Login authentication through a TACACS+ or RADIUS server group, and a TACACS+ server with a key. | 2 | V8.0.0 |
| `ocnos-snmp.policy` | No SNMPv1 or SNMPv2c community (`snmp-server community`). | 1 | V8.0.2 |
| `ocnos-logging.policy` | A remote syslog server (`logging remote server`), and log timestamps not set to seconds or none. | 2 | V8.0.2 |
| `ocnos-services.policy` | NTP authentication with a trusted key (`ntp authenticate`, `ntp trusted-key`), and password encryption (`service password-encryption`). | 2 | V8.3.0 |

The minimum version comes from the methods each file uses: `must_not_match_regex` needs V8.0.2 or later and `evaluate_block` needs V8.3.0 or later. Earlier releases skip the rules they do not support.

Each topic file's `.meta.yaml` lists the references for each rule, where one exists: the NIST SP 800-53 control, the HIPAA 45 CFR section, the NIST CSF 1.1 subcategory and the ISO/IEC 27001:2022 Annex A control.

### Not covered

These checks were proposed and left out, because the capture or the documentation could not settle how they print:

- SSH ciphers: by default OcNOS allows every cipher and prints no cipher line, and the printed form of a configured list is not known.
- exec-timeout: `line vty` and `line console` blocks are not printed at the default, and no default timeout is documented.
- SNMPv3 users: the printed form of an `snmp-server user` line with `auth sha` and `priv aes` is not known.
- Console logging: it is not printed at the default, and the printed form of a change is not known.
- RADIUS servers: the printed form of `radius-server login host ... key` is not known, so the AAA server rule checks TACACS+ only.

## Framework files

Generated from the hardening topic files by `.tooling/scripts/generate_frameworks.py`. Do not edit them: change the topic file or its references and run the generator. Each rule is copied unchanged from its topic file, with its control reference at the start of the description.

| File | Contents | Rules | Minimum rConfig |
|---|---|---|---|
| `ocnos-nist-800-53.policy` | Every topic rule that lists one or more NIST SP 800-53 controls. | 7 | V8.0.2 |
| `ocnos-nist-csf.policy` | Every topic rule that lists one or more NIST CSF 1.1 subcategories. | 1 | V8.0.0 |
| `ocnos-hipaa.policy` | Every topic rule that lists one or more HIPAA 45 CFR 164.312 sections. | 6 | V8.0.2 |
| `ocnos-iso27001.policy` | Every topic rule that lists one or more ISO/IEC 27001:2022 Annex A controls. | 10 | V8.3.0 |

A framework file lists checks relevant to that framework. It is not a certification or a full assessment.

## Supported Models

Tested on a UfiSpace S9510-28DC-B running OcNOS-SP 7.0.0 (build 261, feature code PLUS). The rules use command forms from the OcNOS 6.3 to 6.5 and current SP and DC command references. Other hardware and the DC edition have not been tested.

## Implementation Notes

- OcNOS prints some features at their default: a router with factory settings shows `feature ssh vrf management`, `feature ntp vrf management` and `feature rsyslog`. It does not print `line vty` or `line console` blocks, a default banner, or console logging at their defaults. Telnet is off by default and prints nothing, so the Telnet rule fails only on a `feature telnet` line.
- Some lines end with trailing spaces (for example `logging level nsm 4 ` and the `bfd session` lines). Every rule that ends at the end of a line allows for them with `[ \t]*$`.
- The interface list ends with a stray indented ` exit` after the last interface block, before the next `!`. No rule depends on it.
- `router bgp` separates its address families with indented ` !` lines. rConfig's block splitter ends a scoped block at any line that is `!` once trimmed, so a `scope: ^router bgp` rule would see only the lines before the first address family. Every OcNOS rule is therefore an unscoped regex.
- Every port prints an `interface` block, and unused ports are not shut down: they print as a bare `interface xeN` block with nothing under it. There is therefore no rule that every interface is described or shut down.
- The banner rule accepts any `banner motd` text other than `banner motd default`, which restores the version-string banner. `banner motd` takes a single line of text.
- The remote syslog rules match the stored form `logging remote server <address> <severity> port <port> vrf management`; the standard servers are matched by address, so any severity, port or VRF passes.
- The SNMP location rule accepts `snmp-server location <text>` and `snmp-server location vrf management <text>`, but not `vrf management` with no text.
- Regex rules use the `/.../m` form so that `^` and `$` match at each line of the config.
