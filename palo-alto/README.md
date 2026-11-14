# Palo Alto Networks Policy Templates

Policy definitions for Palo Alto Networks firewalls running PAN-OS.

> [!WARNING]
> These rules have not yet been checked against a real PAN-OS firewall. Their status is `synthetic-tested`: the expected results are recorded against synthetic `show config running` samples rendered from rConfig Pro's PAN-OS demo template and edited by hand in PAN-OS configuration syntax. Before you rely on them, check two things:
> - One real `show config running` from PAN-OS 10.2 or 11.x, to confirm the layout. The samples print one statement per line, as a real firewall is expected to; one sample also keeps the demo template's one-line objects, and every rule gives the same result on both.
> - One `show config running` from a firewall managed by Panorama. Settings pushed from a Panorama template may not appear in `show config running`, which shows the firewall's local configuration. This is unverified. If it is so, a compliant Panorama-managed firewall fails every rule whose setting comes from Panorama.

## Expected config format

Brace format, as returned by `show config running`, rooted at `config {`, with one statement per line ending `;` and two spaces of indentation per level:

```
deviceconfig {
  system {
    hostname dub-fw01;
    login-banner "Authorised use only.";
    service {
      disable-telnet yes;
      disable-http yes;
    }
  }
}
```

This is the command rConfig's PAN-OS demo platform collects, and the output two of the three rConfig PAN-OS connection templates produce. **Set format is not covered.** A connection template that runs `set cli config-output-format set` stores `set deviceconfig system ...` lines, and none of these rules match them.

## Available Policies

| File | Purpose | Rules | Minimum rConfig |
|---|---|---|---|
| `panos-operational-standards.policy` | Drift from your own operational standard, not a hardening check. Example values for NTP servers (192.0.2.10 and 192.0.2.11), syslog servers (192.0.2.20 and 192.0.2.21), DNS servers (192.0.2.30 and 192.0.2.31) and a hostname pattern (`[a-z]{3}-fw[0-9]{2}`, for example `dub-fw01`), plus a login banner, a comment or `link-state down` on every ethernet interface, and an SNMP location. Replace the example values with your own before use. | 7 | V8.3.0 |
| `panos-management-access.policy` | No Telnet or HTTP on the management interface (`disable-telnet no`, `disable-http no`) or in any interface management profile, management access limited to `permitted-ip` addresses, an administrator idle timeout of 1 to 10 minutes, a login banner, and administrator lockout after 1 to 5 failed attempts. | 7 | V8.3.0 |
| `panos-aaa.policy` | Password complexity enabled with a minimum length of 12 or more, and administrator authentication through an authentication profile. | 2 | V8.3.0 |
| `panos-snmp.policy` | No SNMPv2c community (`snmp-community-string`). | 1 | V8.0.2 |
| `panos-logging.policy` | A syslog server profile with a server address, and system and configuration logs forwarded to syslog (`send-syslog` in the `system` and `config` match lists). | 3 | V8.3.0 |

The minimum version comes from the methods each file uses: `must_not_match_regex` needs V8.0.2 or later and `evaluate_block` needs V8.3.0 or later. Earlier releases skip the rules they do not support.

Each topic file's `.meta.yaml` lists the references for each rule, where one exists: the NIST SP 800-53 control, the HIPAA 45 CFR section, the NIST CSF 1.1 subcategory and the ISO/IEC 27001:2022 Annex A control.

## Framework files

Generated from the hardening topic files by `.tooling/scripts/generate_frameworks.py`. Do not edit them: change the topic file or its references and run the generator. Each rule is copied unchanged from its topic file, with its control reference at the start of the description.

| File | Contents | Rules | Minimum rConfig |
|---|---|---|---|
| `panos-nist-800-53.policy` | Every topic rule that lists one or more NIST SP 800-53 controls. | 12 | V8.3.0 |
| `panos-nist-csf.policy` | Every topic rule that lists one or more NIST CSF 1.1 subcategories. | 2 | V8.3.0 |
| `panos-hipaa.policy` | Every topic rule that lists one or more HIPAA 45 CFR 164.312 sections. | 8 | V8.3.0 |
| `panos-iso27001.policy` | Every topic rule that lists one or more ISO/IEC 27001:2022 Annex A controls. | 13 | V8.3.0 |

A framework file lists checks relevant to that framework. It is not a certification or a full assessment.

## Supported Models

Not stated. The rules were written from the PAN-OS 11.1 and 11.2 configure CLI hierarchy and the 10.2 and 11.1 web interface help, and the samples model a PA-3220 on 11.1.4.

## Implementation Notes

- PAN-OS prints only nodes that are present in the configuration. Where the secure value is the default, the rule fails on the insecure value instead of requiring the secure one: Telnet and HTTP on the management interface fail on `disable-telnet no;` and `disable-http no;`, and pass whether or not `disable-telnet yes;` is printed. Where the default is not secure (no permitted IP list, a 60-minute idle timeout, unlimited failed attempts), the rule requires the setting.
- Every statement is matched where it starts a line or follows `{` or `;`, so a rule gives the same result when an object is printed on one line (`admin-lockout { failed-attempts 5; lockout-time 15; }`) as when it is printed over several lines.
- The scoped rules rely on how rConfig matches a `scope:` anchor: against the line with its indentation removed. Every PAN-OS container is indented under `config {`, for example `      deviceconfig {`, so `scope: ^deviceconfig \{$` matches only because the indentation is removed first. Each anchor names one specific container (`deviceconfig`, `password-complexity`, `syslog`, `log-settings`, `dns-setting`, `snmp-system` or an `ethernetN/N` interface), never a generic one: `system {` appears twice (under `deviceconfig` and under `log-settings`) and `config {` up to three times (the root, `deviceconfig setting` and `log-settings`). A scoped rule fails when no block matches, so a firewall with no syslog server profile or no `snmp-system` fails those rules.
- The idle timeout, admin lockout, permitted IP and authentication profile rules are scoped to `deviceconfig`, so a `permitted-ip` list in an interface management profile, or an idle timeout elsewhere (for example GlobalProtect), does not count.
- The system and configuration log rules look for `send-syslog` inside the `system` and `config` match lists under `shared log-settings`. A log forwarding profile that sends traffic and threat logs to syslog does not count.
- The interface rule checks each `ethernetN/N` block. Subinterfaces sit inside their parent's block, under `units`, so a parent passes if any line in its block, including a subinterface, has a `comment`. Aggregate (`ae`) and VLAN interfaces are not checked. Unused ports are usually not in the configuration at all.
- Multi-vsys layouts are not covered. On a multi-vsys firewall, log settings and profiles can sit under each `vsys`, and the scoped rules may see several blocks or none.
- PAN-OS has two NTP server slots, `primary-ntp-server` and `secondary-ntp-server`, so the NTP standard checks both addresses.
- No rule checks the administrator password hash or the SNMPv3 user algorithms: which hash each release writes, and whether default SNMPv3 algorithms are printed, could not be confirmed.
- Regex rules use the `/.../m` form so that `^` and `$` match at each line of the config.
