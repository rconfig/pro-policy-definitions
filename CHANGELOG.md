# Changelog

All notable changes to this repository are recorded here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- Lint for policy files (`.tooling/scripts/lint.py`) that mirrors rConfig Pro's save check, editor check, parser and method list, with a test suite (`.tooling/scripts/test_lint.py`) and a GitHub Actions workflow that runs both on every push and pull request.
- Lint check that every visible top-level folder holds at least one `.policy` file, so Import Templates never shows a folder without templates.
- Allowed method list (`.tooling/scripts/methods.json`), generated from rConfig Pro, with the first rConfig release for each method.
- A `.meta.yaml` file for every policy: title, description, vendor, OS, config format, collection command, kind, minimum rConfig version, status and framework claim.
- Sanitised sample configs in `.tooling/samples/` for Cisco, F5, Fortinet, MikroTik and Juniper.
- Expected results per rule and per sample in `.tooling/expected/`, and `.tooling/scripts/verify_with_pro.php` to check them against rConfig Pro.
- `CONTRIBUTING.md` and this changelog.

### Changed
- Support content (samples, expected results and scripts) lives in the `.tooling/` dot-folder, so rConfig's Import Templates shows only vendor folders with importable templates.
- Juniper templates are withdrawn pending the `display set` rewrite. The drafts moved from `juniper/` to `.drafts/juniper/`, and the `juniper/` folder no longer appears in Import Templates.
- The README now points to `CONTRIBUTING.md` for contribution rules and shows the current repository layout.
- Cisco README: the HIPAA and ISO 27001 policies now need rConfig V8.0.2, because their SNMP community check uses `must_not_match_regex`.
- `.gitattributes` also keeps LF line endings on draft policies, metadata, samples and expected results.
- F5: the WAF logging rule in `f5_bigip_security_baseline.policy` and the F5 samples use the generic log profile name `siem_log_collector` instead of a site-specific one. Results are unchanged.
- Rule descriptions no longer use spaced dashes or em dashes (for example `F5 - …` is now `F5: …`), in the F5 and Fortinet policies and the Juniper drafts. Expected results regenerated to match.
- Cisco README and metadata: the Cisco SAFE and Cisco Security Baseline Guides policies now need rConfig V8.0.2, because their Telnet check uses `must_not_match_regex`.

### Fixed
- Cisco: the Telnet check in all eight benchmark policies (CIS, Cisco SAFE, Cisco Security Baseline Guides, HIPAA, ISO 27001, NIST 800-53, NIST CSF, PCI DSS) used `must_not_match_single_string` with `transport input telnet`, which compares whole lines and so passed on `transport input telnet ssh`. It is now `must_not_match_regex` with `/^\s*transport input .*\b(telnet|all)\b/m`, which fails on any `transport input` line that permits Telnet, including `telnet ssh`, `ssh telnet` and `all`. The Cisco 1921 lab sample, which has `transport input telnet ssh`, now fails this rule as it should.
- Cisco: the console logging check in five benchmark policies (CIS, Cisco SAFE, HIPAA, NIST 800-53, PCI DSS) used `must_not_match_single_string` with `logging console`, which compares whole lines and so passed on `logging console informational`. It is now `must_not_match_regex` with `/^logging console\b/m`, which fails on `logging console` at any level and still passes on `no logging console`. The Catalyst 9500 sample, which has `logging console warnings`, now fails this rule as it should.

### Removed
- README claims the repository could not back up: that every policy is tested and compatible with current rConfig versions, the naming convention example, the licence statement and the promotional closing lines.

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
