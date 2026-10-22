# rConfig Professional Policy Templates

## Overview
Compliance policy definitions for rConfig V8 Professional, organised by vendor. Each policy file comes with machine-readable metadata, and its expected results against sanitised sample configs are recorded in the repository.

> [!IMPORTANT]
> **For Professional Users**: Review the documentation for implementation guidance on Compliance and Policy Definitions at [https://docs.rconfig.com/compliance/overview/](https://docs.rconfig.com/compliance/overview/)

## Repository Structure

```
├── .gitattributes                  # forces LF line endings on policy and sample files
├── .github/workflows/lint.yml      # runs the lint on every push and pull request
├── .tooling/                       # support content, hidden from Import Templates
│   ├── samples/{vendor}/           # sanitised sample configs and samples.yaml
│   ├── expected/{os}-{topic}.yaml  # expected pass or fail per rule, per sample
│   └── scripts/
│       ├── lint.py                 # format, layout and metadata checks, no rConfig Pro needed
│       ├── test_lint.py            # proves each lint check fires
│       ├── methods.json            # allowed methods, generated from rConfig Pro
│       ├── generate_methods.py     # regenerates methods.json
│       ├── generate_frameworks.py  # writes the framework files from the topic files
│       └── verify_with_pro.php     # runs every policy against the samples with rConfig Pro
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE                         # Apache License 2.0
├── README.md
├── cisco/                          # {os}-{topic}.policy, {os}-{topic}.meta.yaml and README.md per vendor
├── f5/
├── fortinet/
├── juniper/
├── mikrotik/
└── pro-base-template/
```

rConfig's Import Templates shows every top-level folder that does not start with a dot, so the only visible folders are vendor folders with importable `.policy` files. Everything else lives in a dot-folder.

Each vendor folder's README lists its policy files, what each covers, the minimum rConfig version and the expected config format.

Files are named `{vendor}/{os}-{topic}.policy`, in lower case with hyphens, for example `cisco/ios-snmp.policy`. Each hardening file covers one topic, such as management access, AAA, SNMP, logging or services. Each `{os}-build-template.policy` is a starting template for a new device build with example values to replace, not a compliance check. Each `{os}-operational-standards.policy` checks drift from your own operational standard (NTP, syslog and DNS servers, login banner, interface descriptions, hostname pattern, SNMP location), using RFC 5737 example values that you replace with your own. `cisco/ios-baseline.policy` is a baseline standard for Cisco IOS and IOS XE, with one block per section (services, DNS, NTP, credentials, HTTP, routing, SSH, SNMP and VTY lines); edit its values to match your own. The `.meta.yaml` of each topic file lists the references for each rule (NIST SP 800-53 control, HIPAA section, NIST CSF subcategory, ISO/IEC 27001:2022 Annex A control) where one exists.

## Topic files and framework files

You can browse the hardening checks by topic or by framework:

- **Topic files**, such as `cisco/ios-snmp.policy`, hold the rules. Each rule appears in exactly one topic file.
- **Framework files**, such as `cisco/ios-nist-800-53.policy`, collect the topic rules that list a reference for one framework: `{os}-nist-800-53`, `{os}-nist-csf`, `{os}-hipaa` and `{os}-iso27001`, for Cisco IOS, FortiOS and Junos. Each rule's description starts with its control reference, for example `NIST AC-17: ...`. A framework with no tagged rules for a vendor has no file.

Framework files are generated from the topic files by `.tooling/scripts/generate_frameworks.py`. **Do not edit them**: change the topic file or its references and run the generator. The lint and CI fail when a framework file differs from the generator output. See [CONTRIBUTING.md](CONTRIBUTING.md#topic-files-and-framework-files).

A framework file lists checks relevant to that framework's controls. It is not a certification or a full assessment, and passing it does not make a device compliant with the framework.

Policy files must use LF line endings. rConfig's parser expects `\n` after each `#[method]` line, so a file saved with CRLF endings loads with zero rules.

## Status

- Juniper templates are written for `display set` format and are `synthetic-tested`: they have not yet been checked against a real Junos device. See `juniper/README.md`.
- Files whose `.meta.yaml` says `status: under-review` carry a `notes:` entry explaining why.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for what a contribution must include and how to run the checks.

## Support and Questions
- **Documentation**: [https://docs.rconfig.com](https://docs.rconfig.com)
- **Email Support**: `info@rconfig.com`
- **Issues**: Use GitHub Issues for template problems or suggestions

## Licence
Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for the full text.
