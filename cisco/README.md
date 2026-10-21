# Cisco Policy Templates

Policy definitions for Cisco IOS and IOS XE devices.

## Expected config format

Running configuration as returned by `show running-config`. Top-level commands start in column 0 and interface or line sub-commands are indented, as on the device.

## Available Policies

| File | Purpose | Rules | Minimum rConfig |
|---|---|---|---|
| `ios-build-template.policy` | Starting template for a new build, not a compliance check. Example values for hostname, timezone, SSH and line access, LAN interface, DHCP, DNS, NAT, ACL, NTP and logging (for example `hostname MyCiscoRouter`, 192.168.88.0/24). Replace them with your own before use. | 10 | V8.0.0 |
| `ios-operational-standards.policy` | Drift from your own operational standard, not a hardening check. Example values for NTP, syslog and DNS servers (192.0.2.10 and 192.0.2.11, 192.0.2.20 and 192.0.2.21, 192.0.2.30 and 192.0.2.31) and a hostname pattern (`[a-z]{3}-(rtr\|sw)[0-9]{2}`, for example `dub-rtr01`), plus a login banner, a description on every interface that is not shut down, and an SNMP location. Replace the example values with your own before use. | 7 | V8.3.0 |
| `ios-management-access.policy` | SSH version 2, no Telnet on any line, no exec-timeout other than the 10 0 default on the console or any VTY line, and MOTD and login banners. | 6 | V8.3.0 |
| `ios-aaa.policy` | AAA enabled, login authentication default on the console and every VTY line, a hashed enable secret, password encryption and no plaintext local passwords. | 6 | V8.3.0 |
| `ios-snmp.policy` | No SNMPv1 or SNMPv2c communities, and an SNMPv3 authPriv group. | 2 | V8.0.2 |
| `ios-logging.policy` | Remote syslog host, millisecond log timestamps, no console logging, buffered logging and a trap severity level. | 5 | V8.0.2 |
| `ios-l2-security.policy` | Proxy ARP disabled on every interface with an IP address, and every interface shut down or described. | 2 | V8.3.0 |
| `ios-routing-authentication.policy` | OSPF message-digest area authentication on every OSPF process, and a BGP neighbor password. | 2 | V8.3.0 |
| `ios-services.policy` | HTTP and HTTPS servers, finger (`service finger` or `ip finger`), TCP and UDP small servers, identd and directed broadcast are not enabled; BOOTP, source routing, CDP and PAD are disabled with their `no` lines. | 11 | V8.0.2 |

The minimum version comes from the methods each file uses: `must_not_match_regex` needs V8.0.2 or later and `evaluate_block` needs V8.3.0 or later. Earlier releases skip the rules they do not support.

Each topic file's `.meta.yaml` lists the published references for each rule, where one exists: the NIST SP 800-53 control, the HIPAA 45 CFR section and the NIST CSF 1.1 subcategory.

## Supported Models

Not stated by the policy authors. The rules use generic IOS and IOS XE command syntax.

## Implementation Notes

- Rules that must hold for every interface, line or OSPF process use `evaluate_block` with a `scope:`, so each matching block is checked on its own. For example, `scope: ^line vty` checks `line vty 0 4` and `line vty 5 15` separately.
- A scoped rule fails when no config block matches its scope. A config with no OSPF process therefore fails the OSPF rule.
- IOS does not print a setting that is at its default. BOOTP, source routing, CDP and PAD are on by default, so the config shows only the `no` line when they are disabled (for example `no ip bootp server`), and those rules require it. Directed broadcast is off by default and `no ip directed-broadcast` is not printed, so that rule fails only when an `ip directed-broadcast` line is present. `exec-timeout 10 0` is the default and is not printed, so the exec-timeout rules fail only when a different `exec-timeout` line is present.
- The operational standards NTP, syslog and DNS rules check that each standard server is configured, not that no other server is. They match the address as a whole word, so `192.0.2.10` does not match `192.0.2.100`, and they accept `ntp server ... prefer`, `ntp server vrf ...` and one `ip name-server` line with several addresses. Escape the dots when you replace an address, for example `192\.0\.2\.10`.
- SNMPv3 users (`snmp-server user`) are not shown in the running config, so no rule checks them.
- Regex rules use the `/.../m` form so that `^` and `$` match at each line of the config.
- `must_not_match_single_string` compares whole lines. For example, `transport input telnet` does not catch `transport input telnet ssh`. The Telnet rule therefore uses `must_not_match_regex` with `/^\s*transport input .*\b(telnet|all)\b/m`, which fails on any `transport input` line that permits Telnet, including `telnet ssh`, `ssh telnet` and `all`.
