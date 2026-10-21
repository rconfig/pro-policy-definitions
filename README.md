# rConfig Professional Policy Templates

## Overview
Compliance policy definitions for rConfig V8 Professional, organised by vendor. Each policy file comes with machine-readable metadata, and its expected results against sanitised sample configs are recorded in the repository.

> [!IMPORTANT]
> **For Professional Users**: Review the documentation for implementation guidance on Compliance and Policy Definitions at [https://docs.rconfig.com/compliance/overview/](https://docs.rconfig.com/compliance/overview/)

## Repository Structure

```
├── .drafts/juniper/                # withdrawn Juniper drafts (*.policy.draft), hidden from Import Templates
├── .gitattributes                  # forces LF line endings on policy and sample files
├── .github/workflows/lint.yml      # runs the lint on every push and pull request
├── .tooling/                       # support content, hidden from Import Templates
│   ├── samples/{vendor}/           # sanitised sample configs and samples.yaml
│   ├── expected/{name}.yaml        # expected pass or fail per rule, per sample
│   └── scripts/
│       ├── lint.py                 # format, layout and metadata checks, no rConfig Pro needed
│       ├── test_lint.py            # proves each lint check fires
│       ├── methods.json            # allowed methods, generated from rConfig Pro
│       ├── generate_methods.py     # regenerates methods.json
│       └── verify_with_pro.php     # runs every policy against the samples with rConfig Pro
├── CHANGELOG.md
├── CONTRIBUTING.md
├── README.md
├── cisco/                          # {name}.policy, {name}.meta.yaml and README.md per vendor
├── f5/
├── fortinet/
├── mikrotik/
└── pro-base-template/
```

rConfig's Import Templates shows every top-level folder that does not start with a dot, so the only visible folders are vendor folders with importable `.policy` files. Everything else lives in a dot-folder.

Each vendor folder's README lists its policy files, what each covers, the minimum rConfig version and the expected config format.

Policy files must use LF line endings. rConfig's parser expects `\n` after each `#[method]` line, so a file saved with CRLF endings loads with zero rules.

## Status

- Juniper templates are withdrawn pending the `display set` rewrite. The drafts are kept in `.drafts/juniper/` as `*.policy.draft` files and do not appear in Import Templates.
- Files whose `.meta.yaml` says `status: under-review` carry a `notes:` entry explaining why.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for what a contribution must include and how to run the checks.

## Support and Questions
- **Documentation**: [https://docs.rconfig.com](https://docs.rconfig.com)
- **Email Support**: `info@rconfig.com`
- **Issues**: Use GitHub Issues for template problems or suggestions

## Licence
A licence for this repository has not been chosen yet.
