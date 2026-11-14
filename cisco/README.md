# Cisco Policy Templates

Policy definitions for Cisco IOS and IOS XE (`ios-*` files) and Cisco IOS XR (`iosxr-*` files). The two sets are separate: IOS rules do not match IOS XR configs, and IOS XR rules do not match IOS configs.

## Cisco IOS and IOS XE

### Expected config format

Running configuration as returned by `show running-config`. Top-level commands start in column 0 and interface or line sub-commands are indented, as on the device.

### Available Policies

| File | Purpose | Rules | Minimum rConfig |
|---|---|---|---|
| `ios-build-template.policy` | Starting template for a new build, not a compliance check. Example values for hostname, timezone, SSH and line access, LAN interface, DHCP, DNS, NAT, ACL, NTP and logging (for example `hostname MyCiscoRouter`, 192.168.88.0/24). Replace them with your own before use. | 10 | V8.0.0 |
| `ios-operational-standards.policy` | Drift from your own operational standard, not a hardening check. Example values for NTP, syslog and DNS servers (192.0.2.10 and 192.0.2.11, 192.0.2.20 and 192.0.2.21, 192.0.2.30 and 192.0.2.31) and a hostname pattern (`[a-z]{3}-(rtr\|sw)[0-9]{2}`, for example `dub-rtr01`), plus a login banner, a description on every interface that is not shut down, and an SNMP location. Replace the example values with your own before use. | 7 | V8.3.0 |
| `ios-baseline.policy` | A baseline standard, not a hardening check: edit the values to match your own. One block per section: services (log and debug timestamps, `no service dhcp`), DNS (`no ip domain lookup`, `ip domain name example.com`, name servers 192.0.2.53 and 198.51.100.53), NTP servers 192.0.2.10 and 192.0.2.11, `aaa new-model` and `ipv6 unicast-routing`, a local `admin` user with a type 9 secret, no `password 0` line, HTTP and HTTPS servers off with local HTTP authentication, a default route, SSH version 2, an SNMPv3 group and host, and `transport input ssh` with no `password` line on every VTY line. | 11 | V8.3.0 |
| `ios-management-access.policy` | SSH version 2, no Telnet on any line, an exec-timeout of 1 to 10 minutes on the console and every VTY line, and MOTD and login banners. | 6 | V8.3.0 |
| `ios-aaa.policy` | AAA enabled, a hashed enable secret, password encryption and no plaintext local passwords. | 4 | V8.0.2 |
| `ios-snmp.policy` | No SNMPv1 or SNMPv2c communities, and an SNMPv3 authPriv group. | 2 | V8.0.2 |
| `ios-logging.policy` | Remote syslog host, millisecond log timestamps (with or without `localtime`, `show-timezone` or `year`), no console logging, buffered logging and a trap severity level. | 5 | V8.0.2 |
| `ios-l2-security.policy` | Proxy ARP disabled on every interface with an IP address, and every interface shut down or described. | 2 | V8.3.0 |
| `ios-routing-authentication.policy` | OSPF message-digest area authentication on every OSPF process, and a BGP neighbor password. | 2 | V8.3.0 |
| `ios-services.policy` | HTTP and HTTPS servers, finger (`service finger` or `ip finger`), TCP and UDP small servers, identd and directed broadcast are not enabled; BOOTP, source routing, CDP and PAD are disabled with their `no` lines. | 11 | V8.0.2 |

The minimum version comes from the methods each file uses: `must_not_match_regex` needs V8.0.2 or later and `evaluate_block` needs V8.3.0 or later. Earlier releases skip the rules they do not support.

Each topic file's `.meta.yaml` lists the references for each rule, where one exists: the NIST SP 800-53 control, the HIPAA 45 CFR section, the NIST CSF 1.1 subcategory and the ISO/IEC 27001:2022 Annex A control.

### Framework files

Generated from the hardening topic files by `.tooling/scripts/generate_frameworks.py`. Do not edit them: change the topic file or its references and run the generator. Each rule is copied unchanged from its topic file, with its control reference at the start of the description. No topic rule lists a NIST CSF subcategory, so there is no `ios-nist-csf.policy`.

| File | Contents | Rules | Minimum rConfig |
|---|---|---|---|
| `ios-nist-800-53.policy` | Every topic rule that lists one or more NIST SP 800-53 controls. | 26 | V8.3.0 |
| `ios-hipaa.policy` | Every topic rule that lists one or more HIPAA 45 CFR 164.312 sections. | 11 | V8.0.2 |
| `ios-iso27001.policy` | Every topic rule that lists one or more ISO/IEC 27001:2022 Annex A controls. | 31 | V8.3.0 |

A framework file lists checks relevant to that framework. It is not a certification or a full assessment.

### Supported Models

Not stated by the policy authors. The rules use generic IOS and IOS XE command syntax.

### Implementation Notes

- Rules that must hold for every interface, line or OSPF process use `evaluate_block` with a `scope:`, so each matching block is checked on its own. For example, `scope: ^line vty` checks `line vty 0 4` and `line vty 5 15` separately.
- A scoped rule fails when no config block matches its scope. A config with no OSPF process therefore fails the OSPF rule.
- IOS does not print a setting that is at its default. BOOTP, source routing, CDP and PAD are on by default, so the config shows only the `no` line when they are disabled (for example `no ip bootp server`), and those rules require it. Directed broadcast is off by default and `no ip directed-broadcast` is not printed, so that rule fails only when an `ip directed-broadcast` line is present. `exec-timeout 10 0` is the default and is not printed, so a line with no `exec-timeout` passes the exec-timeout rules. A line passes with 1 to 9 minutes and 0 to 59 seconds, or with exactly `10 0`. It fails with `0 0` (no timeout), any other value under one minute, more than 10 minutes, or a seconds value of 60 or more.
- The operational standards NTP, syslog and DNS rules check that each standard server is configured, not that no other server is. They match the address as a whole word, so `192.0.2.10` does not match `192.0.2.100`, and they accept `ntp server ... prefer`, `ntp server vrf ...` and one `ip name-server` line with several addresses. Escape the dots when you replace an address, for example `192\.0\.2\.10`.
- The baseline standard's array blocks (`must_match_all_from_array`) pass when each line appears anywhere in the config, as a substring. So `ntp server 192.0.2.10` also matches `ntp server 192.0.2.100`, and a line with more options, such as `ntp server 192.0.2.10 prefer`, still passes. Each name server must be on its own `ip name-server` line. The VTY block uses `evaluate_block` with `scope: ^line vty`, so every VTY line block must have `transport input ssh` exactly and no `password` line.
- SNMPv3 users (`snmp-server user`) are not shown in the running config, so no rule checks them.
- Regex rules use the `/.../m` form so that `^` and `$` match at each line of the config.
- `must_not_match_single_string` compares whole lines. For example, `transport input telnet` does not catch `transport input telnet ssh`. The Telnet rule therefore uses `must_not_match_regex` with `/^\s*transport input .*\b(telnet|all)\b/m`, which fails on any `transport input` line that permits Telnet, including `telnet ssh`, `ssh telnet` and `all`.

## Cisco IOS XR

> [!WARNING]
> These rules have not yet been checked against a real IOS XR router. Their status is `synthetic-tested`: the expected results are recorded against synthetic `show running-config` samples rendered from rConfig Pro's IOS XR demo template and edited by hand in IOS XR command syntax. Before you rely on them, check two things on one of your own routers:
> - On IOS XR 25.3.1 and later, where SSH version 1 can no longer be configured, that `ssh server v2` is still accepted and still printed in `show running-config`. If it is not, the SSH version rule fails on a compliant router.
> - Whether a router with factory logging settings prints a `service timestamps` line at all. The timestamp rule only fails on a `service timestamps log` line without `datetime ... msec`, so it passes when no line is printed; check that your log timestamps include milliseconds.

### Expected config format

Running configuration as returned by `show running-config`. Top-level commands start in column 0, sub-commands are indented one space per level, and every block, including nested blocks, is closed by a `!` line:

```
ssh server v2
logging 192.0.2.20 vrf MGMT severity info port default
line default
 exec-timeout 5 0
 transport input ssh
!
```

This is the command rConfig's IOS XR demo platform collects. rConfig has no IOS XR connection template of its own; IOS XR devices connect with the IOS SSH templates.

### Available Policies

| File | Purpose | Rules | Minimum rConfig |
|---|---|---|---|
| `iosxr-operational-standards.policy` | Drift from your own operational standard, not a hardening check. Example values for NTP servers (192.0.2.10 and 192.0.2.11, in the `ntp` block), syslog hosts (192.0.2.20 and 192.0.2.21), name servers (192.0.2.30 and 192.0.2.31) and a hostname pattern (`[a-z]{3}-(rtr\|sw)[0-9]{2}`, for example `dub-rtr01`), plus a MOTD or login banner, a description on every top-level interface that is not shut down, and an SNMP location. Replace the example values with your own before use. | 7 | V8.3.0 |
| `iosxr-management-access.policy` | SSH version 2 (`ssh server v2`), no Telnet server and no `transport input` that permits Telnet, no line with an exec-timeout outside 1 to 10 minutes, and a MOTD or login banner. | 5 | V8.0.2 |
| `iosxr-aaa.policy` | Login authentication through a TACACS+ or RADIUS server group, no local user with a reversible (`password`) password, and no local user secret with an MD5 (`secret 5`) hash. | 3 | V8.3.0 |
| `iosxr-snmp.policy` | No SNMPv1 or SNMPv2c communities, SNMP users that are all v3 with SHA authentication and AES privacy, and an SNMPv3 authPriv group. | 3 | V8.3.0 |
| `iosxr-logging.policy` | A remote syslog host by address, millisecond log timestamps, and console logging disabled or limited to critical and above. | 3 | V8.0.2 |
| `iosxr-services.policy` | No TFTP server, IPv4 source routing, directed broadcast, proxy ARP or ICMP redirects. | 5 | V8.0.2 |

The minimum version comes from the methods each file uses: `must_not_match_regex` needs V8.0.2 or later and `evaluate_block` needs V8.3.0 or later. Earlier releases skip the rules they do not support.

Each topic file's `.meta.yaml` lists the references for each rule, where one exists: the NIST SP 800-53 control, the HIPAA 45 CFR section, the NIST CSF 1.1 subcategory and the ISO/IEC 27001:2022 Annex A control.

### Framework files

Generated from the IOS XR hardening topic files by `.tooling/scripts/generate_frameworks.py`, in the same way as the IOS framework files. Do not edit them.

| File | Contents | Rules | Minimum rConfig |
|---|---|---|---|
| `iosxr-nist-800-53.policy` | Every IOS XR topic rule that lists one or more NIST SP 800-53 controls. | 17 | V8.3.0 |
| `iosxr-nist-csf.policy` | Every IOS XR topic rule that lists one or more NIST CSF 1.1 subcategories. | 1 | V8.0.0 |
| `iosxr-hipaa.policy` | Every IOS XR topic rule that lists one or more HIPAA 45 CFR 164.312 sections. | 11 | V8.3.0 |
| `iosxr-iso27001.policy` | Every IOS XR topic rule that lists one or more ISO/IEC 27001:2022 Annex A controls. | 18 | V8.3.0 |

A framework file lists checks relevant to that framework. It is not a certification or a full assessment.

### Supported Models

Not stated. The rules were written from the Cisco NCS 5500, NCS 540 and NCS 560 command references for 64-bit IOS XR (Release 6.0 to 26.x), and the samples model an ASR 9901 on 7.9.2. 32-bit IOS XR (4.x and 5.x on older ASR 9000 and CRS) was not checked.

### Implementation Notes

- Almost every IOS XR rule is an unscoped regex rather than an `evaluate_block` with a `scope:`. rConfig's block splitter (`app/Services/Compliance/Definitions/Engine/BlockSplitter.php` in rConfig Pro) ends an indented block at any line that is `!` once trimmed, so the indented ` !` that closes a nested sub-block also ends the outer block. On IOS XR, where every nested block has its own ` !`, a scoped rule would only see a block up to its first nested sub-block. For the same reason there is no BGP neighbour password rule: the `router bgp` block is cut short at its first neighbour group. The one scoped rule, "no local user has a reversible password" (`scope: ^username`), works because `username` blocks have no nested sub-blocks.
- The splitter also matches the `scope:` anchor against the line with its indentation removed, so `scope: ^interface` would also pick up the indented `interface` lines under `router isis` and `mpls ldp`. The operational standards interface rule therefore uses a regex anchored at column 0 that fails on any top-level `interface` block (other than `interface preconfigure`) with neither a ` description` nor a ` shutdown` line before its closing `!`.
- IOS XR does not print a setting that is at its default. The Telnet and TFTP servers, IPv4 source routing, directed broadcast, proxy ARP and ICMP redirects are all off by default and print nothing, so those rules fail only on the enabling line. `exec-timeout 10 0` is the default, so a line with no `exec-timeout` passes; a line passes with 1 to 9 minutes and 0 to 59 seconds, or exactly `10` or `10 0`, and fails with `0 0`, more than 10 minutes, or 60 or more seconds. The exec-timeout rule checks every `exec-timeout` line in the config (console, `line default` and any `line template`), not one named line, because a router that has never set one has no `line default` block to scope on.
- `ssh server v2` is not the default (the default server accepts version 2 and falls back to version 1), so the SSH rule requires it.
- Console logging is on at informational by default and not printed, so the console rule requires a `logging console` line with `disable`, `critical`, `alerts` or `emergencies`.
- SNMP users are printed in `show running-config` on IOS XR (unlike IOS), so the SNMP user rule checks them: at least one v3 user with `auth sha` and `priv aes`, and no user that is v1, v2c or `remote`, uses `auth md5`, uses `priv des56` or `priv 3des`, or has no `priv` at all.
- The remote syslog rule matches `logging` followed by an IPv4 or IPv6 address. A syslog host given by name is not matched, because a name cannot be told apart from keywords such as `logging buffered`.
- The operational standards NTP rule matches ` server` lines with the standard address, with or without `vrf` and `ipv4`. It does not check that the line is inside the `ntp` block, so a TACACS+ group ` server` line with the same address would also count. Escape the dots when you replace an address, for example `192\.0\.2\.10`.
- The `no local user has a reversible password` rule fails on a `password` line under any `username`; use `secret` instead. BGP `password encrypted` and key chain `key-string password` lines are outside `username` blocks and do not count.
- Regex rules use the `/.../m` form so that `^` and `$` match at each line of the config.
