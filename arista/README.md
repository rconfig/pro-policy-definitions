# Arista Policy Templates

Policy definitions for Arista EOS switches.

> [!WARNING]
> These rules have not yet been checked against a real EOS switch. Their status is `synthetic-tested`: the expected results are recorded against synthetic `show running-config` samples rendered from rConfig Pro's EOS demo template and edited by hand in EOS command syntax. Before you rely on them, check two things on one of your own switches:
> - That `idle-timeout` is printed before the `vrf` sub-block under `management ssh`. The idle timeout rule only sees the lines before the first nested `!` (see the notes).
> - The default syslog trap level, from `show running-config all | include logging trap`. It is not stated in the EOS manual, so there is no trap level rule yet.

## Expected config format

Running configuration as returned by `show running-config`. Top-level commands start in column 0, sub-commands are indented three spaces per level, and each block is closed by a `!` line. A nested sub-block has its own indented `!`:

```
logging vrf MGMT host 192.0.2.20
!
management ssh
   idle-timeout 10
   authentication protocol password
   !
   vrf MGMT
      no shutdown
!
```

This is the command rConfig's EOS demo platform collects, and the retrieval command the Arista connection templates name. EOS prints only settings that differ from the default; `show running-config all` prints the defaults as well, and the rules are not written for that output.

## Available Policies

| File | Purpose | Rules | Minimum rConfig |
|---|---|---|---|
| `eos-operational-standards.policy` | Drift from your own operational standard, not a hardening check. Example values for NTP servers (192.0.2.10 and 192.0.2.11), syslog hosts (192.0.2.20 and 192.0.2.21), name servers (192.0.2.30 and 192.0.2.31) and a hostname pattern (`[a-z]{3}-(rtr\|sw)[0-9]{2}`, for example `dub-sw01`), plus a login banner, a description on every interface that is not shut down, and an SNMP location. Replace the example values with your own before use. | 7 | V8.3.0 |
| `eos-management-access.policy` | No Telnet (`management telnet` with `no shutdown`), an SSH idle timeout of 1 to 10 minutes, no SSH `cipher` or `mac` line with a CBC, 3DES, arcfour, blowfish, MD5 or SHA-1 algorithm, and a login banner. | 4 | V8.3.0 |
| `eos-aaa.policy` | The root account disabled, login authentication through a server group with local fallback, no local user with `nopassword`, and command accounting to a server group. | 4 | V8.0.2 |
| `eos-snmp.policy` | No SNMPv1 or SNMPv2c communities, an SNMPv3 authPriv group, and no SNMPv3 user with MD5 authentication or DES privacy. | 3 | V8.0.2 |
| `eos-logging.policy` | A remote syslog host, in any VRF, and high-resolution log timestamps. | 2 | V8.0.0 |
| `eos-services.policy` | The eAPI does not serve plain HTTP (`protocol http` under `management api http-commands`). | 1 | V8.0.2 |

The minimum version comes from the methods each file uses: `must_not_match_regex` needs V8.0.2 or later and `evaluate_block` needs V8.3.0 or later. Earlier releases skip the rules they do not support.

Each topic file's `.meta.yaml` lists the references for each rule, where one exists: the NIST SP 800-53 control, the HIPAA 45 CFR section, the NIST CSF 1.1 subcategory and the ISO/IEC 27001:2022 Annex A control.

## Framework files

Generated from the hardening topic files by `.tooling/scripts/generate_frameworks.py`. Do not edit them: change the topic file or its references and run the generator. Each rule is copied unchanged from its topic file, with its control reference at the start of the description.

| File | Contents | Rules | Minimum rConfig |
|---|---|---|---|
| `eos-nist-800-53.policy` | Every topic rule that lists one or more NIST SP 800-53 controls. | 12 | V8.3.0 |
| `eos-nist-csf.policy` | Every topic rule that lists one or more NIST CSF 1.1 subcategories. | 1 | V8.0.0 |
| `eos-hipaa.policy` | Every topic rule that lists one or more HIPAA 45 CFR 164.312 sections. | 8 | V8.0.2 |
| `eos-iso27001.policy` | Every topic rule that lists one or more ISO/IEC 27001:2022 Annex A controls. | 14 | V8.3.0 |

A framework file lists checks relevant to that framework. It is not a certification or a full assessment.

## Supported Models

Not stated. The rules were written from the EOS User Manual for 4.36.2F and 4.37.0F, and the samples model a DCS-7280CR3-32P4 on 4.32.2F. Older 4.2x releases may differ in their default SSH ciphers and in how `snmp-server user` lines are printed.

## Implementation Notes

- EOS indents sub-commands three spaces per level and closes each block with `!`. Rules that must look inside one block use `evaluate_block` with a `scope:`, which checks each matching block on its own.
- rConfig's block splitter ends a scoped block at the first line that is `!` once trimmed, including the indented `   !` that closes a nested sub-block. A scoped rule therefore sees only the lines before the first nested sub-block. The SSH idle timeout rule (`scope: ^management ssh$`) works because EOS prints `idle-timeout` before the `vrf` sub-block; if `idle-timeout` were printed after it, the rule would fail on a compliant switch. The other management access rules are unscoped regexes for the same reason.
- The splitter also matches a `scope:` anchor against the line with its indentation removed. No EOS sub-command starts with `interface` or `management ssh`, so the two anchors used here match only top-level lines.
- Telnet is off by default, and a switch at default prints no `management telnet` block at all. The Telnet rule fails only on a `no shutdown` line under `management telnet` (including under a `vrf` inside it), so it does not depend on the block being printed.
- The SSH idle timeout default is 0 (no timeout) and is not printed, so the rule needs an explicit `idle-timeout` of 1 to 10 minutes. A switch with no `management ssh` block fails it.
- The EOS manual gives the `cipher` and `mac` syntax under `management ssh` but not the default list, so the cipher rule fails only on an explicit weak `cipher` or `mac` line. It does not catch a weak algorithm in an unprinted default list on an older release.
- The root account is disabled by default. The root rule fails on any line starting `aaa root ` (for example `aaa root secret ...` or `aaa root nopassword`), so it passes whether or not `no aaa root` is printed.
- SNMPv3 users are printed in `show running-config` on EOS (unlike IOS), in the localized form `snmp-server user <user> <group> v3 localized <engine ID> auth ... priv ...`, so the SNMP user rule can see them.
- `banner login` is printed on its own line, followed by the banner text and a line with `EOF`. The banner rules match the `banner login` line only.
- The operational standards interface rule checks every `interface` block. Unconfigured Ethernet ports are printed as a bare `interface EthernetN` block with nothing under it, so they fail the rule until you shut them down or describe them. Loopback, Management and Vxlan interfaces are checked too.
- The operational standards NTP, syslog and DNS rules check that each standard server is configured, with or without `vrf <name>`, not that no other server is. Escape the dots when you replace an address, for example `192\.0\.2\.10`.
- Regex rules use the `/.../m` form so that `^` and `$` match at each line of the config.
