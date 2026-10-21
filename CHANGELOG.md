# Changelog

All notable changes to this repository are recorded here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [1.3.0] - 2026-10-21

### Added
- Framework files, generated from the hardening topic files by the new `.tooling/scripts/generate_frameworks.py`, so you can assign checks by topic or by framework. Each collects every topic rule that lists a reference for one framework, copied unchanged, with the control reference at the start of its description (for example `NIST AC-17: ...`). Each has a `.meta.yaml` with `kind: framework`, `generated: true`, its source topic files and the highest minimum version among its rules. A framework with no tagged rules for a vendor gets no file. Eleven files:
  - `cisco/ios-nist-800-53` (26 rules), `ios-hipaa` (11), `ios-iso27001` (31). No Cisco rule lists a NIST CSF subcategory, so there is no `ios-nist-csf`.
  - `fortinet/fortios-nist-800-53` (8), `fortios-nist-csf` (2), `fortios-hipaa` (7), `fortios-iso27001` (10).
  - `juniper/junos-nist-800-53` (10), `junos-nist-csf` (2), `junos-hipaa` (10), `junos-iso27001` (15).
- ISO/IEC 27001:2022 Annex A references (`iso27001`) on the Cisco, FortiOS and Junos hardening topic rules where the control clearly covers the check: A.5.17 Authentication information, A.8.5 Secure authentication, A.8.9 Configuration management, A.8.15 Logging, A.8.20 Networks security and A.8.24 Use of cryptography. 56 of 59 rules are mapped; console logging (Cisco and Junos) and the Junos UTC time zone rule are not. Build templates and operational standards files are not mapped.
- Lint checks for framework files: `kind: framework` needs `generated: true` and `sources`; every framework file must match the generator output (`generate_frameworks.py --check`, also a CI step), so hand edits fail; and every framework rule's expected results must equal those of its source topic rule. `test_lint.py` covers each check.
- Expected results for the framework files. Every framework rule gives the same result as its source topic rule on every sample.

### Changed
- `kind` in `.meta.yaml` can be `framework`, for generated files only. The references header in the topic `.meta.yaml` files lists `iso27001` and says the references are relevant controls, not a claim that the rule fully meets them.
- README, vendor READMEs and `CONTRIBUTING.md` explain topic files and framework files, that framework files are generated and must not be edited by hand, and that they list relevant checks and are not a certification or a full assessment.

## [1.2.0] - 2026-10-21

### Added
- Juniper topic files for `display set` format (`show configuration | display set`), `kind: hardening`, `status: synthetic-tested`: `juniper/junos-management-access` (5 rules), `junos-aaa` (2), `junos-snmp` (2), `junos-logging` (5), `junos-services` (2) and `junos-interfaces` (1), each with a `.meta.yaml` and expected results, and a `juniper/README.md` that says the rules have not yet been checked against a real Junos device. They replace the brace-format drafts: each rule appears once, without the local control IDs.
- Juniper samples `ex2300-junos232-hardened-synthetic.txt` and `ex2300-junos151-unhardened-synthetic.txt`, built from rConfig Pro's Junos demo generator. Every Juniper rule passes on the hardened sample and fails on the unhardened one, and one edit per rule to the hardened sample fails that rule and no other.
- Cisco sample `c9500-iosxe179-hardened-synthetic.txt` and FortiOS sample `fg60f-fortios744-hardened-synthetic.txt`, built from Pro's demo generators to pass every rule in the Cisco and FortiOS hardening topic files.
- MikroTik sample `c52ig-routeros7153-unhardened-synthetic.txt`, an unhardened `/export` from Pro's RouterOS CPE generator.
- FortiOS management access: two rules on `config system global`, each on its own, `set strong-crypto enable` and `set pre-login-banner enable`. Both settings are in the FortiOS 7.4.4 CLI Reference. They replace the strong crypto and pre-login banner checks that were part of the removed admin HTTPS and MOTD rules. `fortinet/fortios-management-access` now has four rules.

### Changed
- Expected results for every Cisco, FortiOS, RouterOS and base template policy now include the new samples. Rules with the same result on every sample went from 70 to 55. Two of the 55 are new in this release and pass on every sample: the Cisco timestamp rule, because none of the four Cisco samples logs without `msec`, and the FortiOS strong crypto rule, because all three FortiOS samples set `set strong-crypto enable`.
- Juniper rules compared with the drafts:
  - The two authentication order rules are one rule that accepts RADIUS or TACACS+ first and needs `password` last, instead of exactly `[ radius tacplus password ]`.
  - SSH enabled and SSH version 2 are one rule that fails on `protocol-version` with `v1`, because version 2 is the Junos default and is not printed.
  - The SSH cipher and MAC rule fails on weak algorithms instead of requiring one exact list.
  - The plain-text-password rule is replaced by a rule that fails on an MD5 (`$1$`) password hash, because Junos never stores `plain-text-password`.
  - The syslog rules (`any info` or `any notice`, `authorization info`, `time-format millisecond`, in several combinations) are three rules, and the two console logging rules are one.
  - The UTC rule fails only on a `set system time-zone` line other than `UTC`, the default.
  - The redirects and source routing rule checks `set system no-redirects` only; the `family inet no-source-route-option` statement it also required could not be confirmed as a Junos statement.
  - The "an interface is disabled" rule is now "every interface is disabled or has a description", as in `cisco/ios-l2-security`.
  - NIST CSF references PR.AC-2 (SSH and Telnet), PR.PT-1 (insecure services) and ID.AM-1 (login banner) are not recorded, as for FortiOS.
- The MikroTik and Fortinet `samples.yaml` files no longer list a missing unhardened or hardened sample as a gap.
- Cisco logging: the timestamp rule passes `service timestamps log datetime msec` with other options, for example `localtime show-timezone` or `year`. It used `must_match_single_string`, which compares whole lines, so it failed on those forms. It is now `must_match_regex`. The Catalyst 9500 sample (`... msec localtime show-timezone`) now passes it.
- Cisco exec-timeout (console and every VTY line): any timeout from 1 to 10 minutes passes (1 to 9 minutes with 0 to 59 seconds, or `10 0`), and so does no `exec-timeout` line (the 10 0 default). `0 0`, any other value under one minute and anything over 10 minutes fail. Before, any value other than `10 0` failed, including stricter ones such as `5 0`. The hardened Catalyst 9500 sample now uses `exec-timeout 5 0`.

### Removed
- `.drafts/juniper/`: the brace-format Juniper drafts, now replaced by the `juniper/` topic files.
- Cisco AAA: the console and VTY `login authentication default` rules. IOS does not print `login authentication default`, because it is the default method list, so the rules failed on compliant configs. `cisco/ios-aaa` now has four rules and needs rConfig V8.0.2.
- FortiOS management access: the admin HTTPS, HTTP and strong crypto rule (`set admin-https`, `set admin-http`), the login banner and MOTD rule (`set motd`) and the admin address group rule (`set admin-addrgrp`). None of these four settings is in the FortiOS 7.4.4 CLI Reference, so the rules could not pass on a real FortiGate. The hardened FortiGate 60F sample no longer has those lines or the address group added for `admin-addrgrp`.

## [1.1.0] - 2026-10-21

### Added
- Operational standards files `cisco/ios-operational-standards` and `fortinet/fortios-operational-standards` (`kind: operational`, `status: synthetic-tested`, rConfig V8.3.0). Each has seven rules that check drift from your own standard: NTP, syslog and DNS servers, a login banner (FortiOS: pre-login banner), a description on every interface that is not shut down (FortiOS: not set to status down), a hostname naming pattern, and an SNMP location. The servers and hostname pattern are RFC 5737 and example values, and each rule description says what to replace.
- Synthetic samples `ios157-operational-standards-synthetic.txt` (Cisco) and `fortios744-operational-standards-synthetic.txt` (Fortinet), built from those example values. Expected results for every Cisco and FortiOS policy now include them; no existing result changed.

### Fixed
- FortiOS management access: the login banner rule checked `set login-banner enable`, which is not a FortiOS `config system global` setting, so it could never pass. It now checks `set pre-login-banner enable`, with `set motd enable` as before.

## [1.0.0] - 2026-10-21

### Added
- Lint for policy files (`.tooling/scripts/lint.py`) that mirrors rConfig Pro's save check, editor check, parser and method list, with a test suite (`.tooling/scripts/test_lint.py`) and a GitHub Actions workflow that runs both on every push and pull request.
- Lint check that every visible top-level folder holds at least one `.policy` file, so Import Templates never shows a folder without templates.
- Allowed method list (`.tooling/scripts/methods.json`), generated from rConfig Pro, with the first rConfig release for each method.
- A `.meta.yaml` file for every policy: title, description, vendor, OS, config format, collection command, kind, minimum rConfig version, status and framework claim.
- Sanitised sample configs in `.tooling/samples/` for Cisco, F5, Fortinet, MikroTik and Juniper.
- Expected results per rule and per sample in `.tooling/expected/`, and `.tooling/scripts/verify_with_pro.php` to check them against rConfig Pro.
- `CONTRIBUTING.md` and this changelog.
- Topic-based hardening files for Cisco IOS (`cisco/ios-management-access`, `ios-aaa`, `ios-snmp`, `ios-logging`, `ios-l2-security`, `ios-routing-authentication`, `ios-services`) and FortiOS (`fortinet/fortios-management-access`, `fortios-aaa`, `fortios-snmp`, `fortios-logging`). They replace the per-framework files: each rule appears once, its description says plainly what it checks, and its `.meta.yaml` lists the rule's published references (NIST SP 800-53 control, HIPAA 45 CFR section, NIST CSF 1.1 subcategory) under `rules`.
- `LICENSE`: the repository is licensed under the Apache License, Version 2.0, and the README says so.
- RouterOS sample `routeros7153-build-template-synthetic.txt`, a hardened synthetic `/export` config built from the build template's example values, so the expected results record every RouterOS template rule passing.

### Changed
- Support content (samples, expected results and scripts) lives in the `.tooling/` dot-folder, so rConfig's Import Templates shows only vendor folders with importable templates.
- Juniper templates are withdrawn pending the `display set` rewrite. The drafts moved from `juniper/` to `.drafts/juniper/`, and the `juniper/` folder no longer appears in Import Templates.
- The README now points to `CONTRIBUTING.md` for contribution rules and shows the current repository layout.
- Cisco README: the HIPAA and ISO 27001 policies now need rConfig V8.0.2, because their SNMP community check uses `must_not_match_regex`.
- `.gitattributes` also keeps LF line endings on draft policies, metadata, samples and expected results.
- F5: the WAF logging rule in `f5_bigip_security_baseline.policy` and the F5 samples use the generic log profile name `siem_log_collector` instead of a site-specific one. Results are unchanged.
- Rule descriptions no longer use spaced dashes or em dashes (for example `F5 - …` is now `F5: …`), in the F5 and Fortinet policies and the Juniper drafts. Expected results regenerated to match.
- Cisco README and metadata: the Cisco SAFE and Cisco Security Baseline Guides policies now need rConfig V8.0.2, because their Telnet check uses `must_not_match_regex`.
- Files are named `{vendor}/{os}-{topic}.policy`, in lower case with hyphens; each `.meta.yaml` and expected results file uses the same name. Renamed:
  - `cisco/cisco_ios_base` to `cisco/ios-build-template`
  - `fortinet/fortigate_base` to `fortinet/fortios-build-template`
  - `mikrotik/mikrotik_base` to `mikrotik/routeros-build-template`
  - `f5/f5_bigip_security_baseline` to `f5/bigip-security-baseline` (content unchanged)
  - `f5/f5_bigip_ssl_virtual_hardening` to `f5/bigip-ssl-virtual-hardening` (content unchanged)
- The three build templates are described as starting templates to edit, not compliance checks, in their README rows and `.meta.yaml`. None of them is `under-review` any more.
- Rules that must hold for every interface, line, OSPF process or FortiOS section now use `evaluate_block` with a `scope:`, so every matching block is checked. Before, `match_code_block_from_array` checked only the first matching block and the lines directly after it, and `match_code_block_flexible` checked from the first match to the end of a Cisco config. Converted: VTY and console exec-timeout, console and VTY `login authentication default`, proxy ARP per interface, interfaces shut down, OSPF authentication, and FortiOS admin HTTPS and strong crypto, admin idle timeout, login banner and MOTD, admin address group, RADIUS server, password policy, SNMPv3 users, syslog setting and syslog filter. Files that use it need rConfig V8.3.0.
- Interface rules now say which interfaces they cover: proxy ARP is checked on interfaces with an IP address, and the "unused interfaces shut down" rules accept an interface that is shut down or has a description.
- FortiOS: the syslog severity rules (`information` in some framework files, `notice` in others) are merged into one rule that accepts either, because both cannot pass on one config.
- FortiOS build template: the hostname, timezone and NAT rules used `must_match_single_string` with a multi-line body, which always fails. They now use `must_match_all_from_array` with the same body.
- `CONTRIBUTING.md` describes the naming convention, plain descriptions without local IDs, and the `rules` references field.
- RouterOS build template: every rule is rewritten to match `/export` output, a section line (for example `/ip service`) followed by a `set` or `add` line in that section, keeping each rule's intent and example values. Arguments may appear in any order, with other arguments between them and ` \` line continuations. The NTP rule accepts the RouterOS 6 (`primary-ntp=`, `secondary-ntp=`) or RouterOS 7 (`/system ntp client servers`) form. The template now uses `evaluate_block` and needs rConfig V8.3.0, and its status is `synthetic-tested`.
- Cisco services: BOOTP, source routing, CDP and PAD are on by default and IOS does not print the enabling line, so the rules that checked `ip bootp server`, `ip source-route`, `cdp run` and `service pad` were absent always passed. They now require `no ip bootp server`, `no ip source-route`, `no cdp run` and `no service pad`.
- Cisco exec-timeout: `exec-timeout 10 0` is the IOS default and is not printed, so the console and VTY rules failed on compliant configs. They now fail only when an `exec-timeout` other than `10 0` is set.
- FortiOS password policy: the rule accepts `set minimum-length 12` (FortiOS 7) as well as `set min-length 12`.
- Cisco services: the directed broadcast rule required a `no ip directed-broadcast` line, which IOS does not print because directed broadcast is off by default. It now fails only when an `ip directed-broadcast` line is present on any interface, with or without an access list.
- Cisco services: the finger rule checked only `service finger`, but IOS 12.1 and later configure finger with `ip finger`. It now fails on either line. `cisco/ios-services` needs rConfig V8.0.2, because both rules use `must_not_match_regex`.

### Fixed
- Cisco: the Telnet check in all eight benchmark policies (CIS, Cisco SAFE, Cisco Security Baseline Guides, HIPAA, ISO 27001, NIST 800-53, NIST CSF, PCI DSS) used `must_not_match_single_string` with `transport input telnet`, which compares whole lines and so passed on `transport input telnet ssh`. It is now `must_not_match_regex` with `/^\s*transport input .*\b(telnet|all)\b/m`, which fails on any `transport input` line that permits Telnet, including `telnet ssh`, `ssh telnet` and `all`. The Cisco 1921 lab sample, which has `transport input telnet ssh`, now fails this rule as it should.
- Cisco: the console logging check in five benchmark policies (CIS, Cisco SAFE, HIPAA, NIST 800-53, PCI DSS) used `must_not_match_single_string` with `logging console`, which compares whole lines and so passed on `logging console informational`. It is now `must_not_match_regex` with `/^logging console\b/m`, which fails on `logging console` at any level and still passes on `no logging console`. The Catalyst 9500 sample, which has `logging console warnings`, now fails this rule as it should.

### Removed
- README claims the repository could not back up: that every policy is tested and compatible with current rConfig versions, the naming convention example, the licence statement and the promotional closing lines.
- Per-framework hardening files, with their `.meta.yaml` and expected results. Their rules moved to the topic files, and the local control IDs (`CIS-x`, `SAFE-x`, `SBG-x`, `HIPAA-x`, `ISO-x`, `NIST-x`, `CSF-x`, `PCI-x`, `BASE-x`) were dropped:
  - `cisco/cisco_ios_CIS_benchmark`, `cisco_ios_CISCOSAFE_benchmark`, `cisco_ios_CISCOSBG_benchmark`, `cisco_ios_HIPAA_benchmark`, `cisco_ios_ISO27K_benchmark`, `cisco_ios_NIST_benchmark`, `cisco_ios_NISTCSF_benchmark`, `cisco_ios_PCIDSS_benchmark`
  - `fortinet/fortinet_fortios_base`, `fortinet_fortios_CIS_benchmark`, `fortinet_fortios_FORTINETSAFE_benchmark`, `fortinet_fortios_HIPAA_benchmark`, `fortinet_fortios_ISO27K_benchmark`, `fortinet_fortios_NIST_benchmark`, `fortinet_fortios_NISTCSF_benchmark`, `fortinet_fortios_PCIDSS_benchmark`
- Duplicate rules: Cisco went from 134 rules in eight files to 37 distinct rules, and FortiOS from 64 rules in eight files to 14. After the removals below, the topic files hold 31 Cisco rules and 11 FortiOS rules.
- Build template rules that can never pass or that required SNMP community `public`:
  - Cisco: the `write erase` / `reload` rule, the SNMP rule (`snmp-server community public RO`), and three lines of the secure access rule: `username admin privilege 15 secret YourStrongPassword` (the running config shows the hashed secret), `line console 0` (shown as `line con 0`) and `crypto key generate rsa general-keys modulus 2048` (an exec command).
  - FortiOS: the `execute factoryreset` rule, the SNMP rule (community `public`), and the `config system admin` lines with `set password YourStrongPassword` (shown encrypted) from the secure access rule.
  - RouterOS: the `/system reset-configuration` rule, the SNMP rule (`trap-community=public`), and the `/user add ... password=` and `/user set 0 password=` lines from the secure access rule.
- Overlapping rules that a stronger rule already covers: in `cisco/ios-l2-security`, "at least one `no ip proxy-arp` line" and "every FastEthernet interface is shut down or has a description"; in `fortinet/fortios-management-access`, the combined admin HTTPS, strong crypto and idle timeout rule, and the "telnet" and "telnet or http" `allowaccess` rules.
- Cisco SNMP: the SNMPv3 user rule, because `snmp-server user` lines are not shown in the running config.
- FortiOS references to NIST CSF subcategories that do not fit their rules: ID.AM-1 on the login banner rule, DE.CM-2 on the syslog severity rule, PR.DS-1 on both SNMP rules and PR.PT-1 on the insecure protocols rule.

## 2026-10-21

### Cisco
- Converted `cisco_ios_base.policy` from CRLF to LF line endings, so rConfig now loads its rules.
- Removed banner and section comments that made the files fail rConfig's save check.
- Gave every rule its own description where several rules shared one.
- Delimited every regex rule with `/.../m`, so `^` and `$` match at each line rather than only at the start of the file. The plaintext password checks, which always passed before, now detect `password 0` users.
- The SNMP community check now catches any `snmp-server community` line, rather than only a literal `*`.
- The BGP neighbour password check now matches indented `neighbor` lines.
- The `logging host` and `logging buffered` checks now pass when the line exists.
- Corrected descriptions that did not match their rules: proxy ARP rather than gratuitous ARP, and exec-timeout set to 10 minutes rather than "10 minutes or less".

### F5
- Removed header comments that made both files fail rConfig's save check.
- The TLS 1.0 check no longer passes on `no-tlsv1.1`, `no-tlsv1.2` or `no-tlsv1.3`, and TLS 1.1 is now checked as the description says.

### Fortinet
- Converted `fortigate_base.policy` from CRLF to LF line endings, so rConfig now loads its rules.
- Removed header comments that made the files fail rConfig's save check.
- Gave every rule its own description where several rules shared one.
- Delimited every regex rule with `/.../m`. The Telnet, HTTP and SNMP community checks, which always passed before, now inspect every line.
- Corrected descriptions that promised more than their rules check: admin timeout and password length now state the exact value, BASE-2 no longer mentions SSH, and ISO-A9-2 names RADIUS only.

### Juniper
- Withdrew all Juniper policies while they are rewritten for `display set` format, which is what rConfig collects. They are kept as `*.policy.draft` files and do not appear in Import Templates.

### MikroTik
- Converted `mikrotik_base.policy` from CRLF to LF line endings, so rConfig now loads its rules.
- The DNS, SNMP and NTP rules now load: they used a list method with a one-line body, which rConfig skips.
- Corrected descriptions that named the wrong method.

### Base template
- Converted `defaultPolicyDefinition.policy` from CRLF to LF line endings, so rConfig now loads its rules.
- Corrected descriptions that said "Enable" for rules that disable IP source routing and ICMP redirects.

### Repository
- Added `.gitattributes` to keep LF line endings on policy files.
- Added a README per vendor folder and rewrote the repository structure section of the main README.
