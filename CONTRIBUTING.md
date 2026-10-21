# Contributing

Thank you for contributing a policy definition. This page sets out what a contribution must include and how to run the checks before you open a pull request.

## What a contribution must include

1. **The policy file**, `{vendor}/{os}-{topic}.policy`, in the format below. Names are lower case with hyphens, for example `cisco/ios-snmp.policy`. Add a rule to the existing topic file when one fits.
2. **A metadata file**, `{vendor}/{os}-{topic}.meta.yaml`, next to the policy file.
3. **Sample configs**: at least one hardened and one non-hardened sample in `.tooling/samples/{vendor}/` with the same `config_format` as the policy, each listed in that folder's `samples.yaml`. Reuse existing samples where they fit.
4. **Expected results**, `.tooling/expected/{os}-{topic}.yaml`, generated with rConfig Pro and reviewed by you.
5. **A passing lint** (`python3 .tooling/scripts/lint.py`).
6. A row in the vendor folder's `README.md` and an entry under "Unreleased" in `CHANGELOG.md`.

If you cannot run rConfig Pro, open the pull request without the expected results file and say so; a maintainer will generate it. The lint will report it as missing until then.

## Policy file format

Each rule is three or more lines: a `//` description, a `#[method]` directive on the very next line, then the rule body. The description says plainly what the rule checks, with no local control IDs; published references go in the metadata file.

```
// AAA is enabled (aaa new-model)
#[must_match_single_string]
aaa new-model
```

The lint enforces these rules, each of which mirrors how rConfig Pro reads the file:

- LF line endings, no byte order mark, and a newline at the end of the file.
- Every `//` line is followed directly by a `#[` line, with exactly one `#[` per description, and no blank line between the description, the directive and the first body line.
- No other comments: `/* */` is not supported, and `//` must not appear anywhere except at the start of a description line, because rConfig splits the file on every `//`.
- The method is one of those in `.tooling/scripts/methods.json`.
- `must_match_regex` and `must_not_match_regex` bodies, and `regex:` leaves in `evaluate_block`, are delimited, for example `/^logging host \S+/m`. Use the `m` flag when the pattern uses `^` or `$`, so they anchor to each line.
- Array methods (`must_match_all_from_array` and the others listed under `array_methods` in `.tooling/scripts/methods.json`) have a body of two or more lines.
- `evaluate_block` bodies are valid YAML and a valid rule tree.

## Repository layout and Import Templates

rConfig's Import Templates clones this repository and shows every top-level folder that does not start with a dot, then lists the `*.policy` files directly inside the chosen folder. So:

- Each visible top-level folder is a vendor folder with at least one `.policy` file. The lint checks this.
- Support material lives in dot-folders, which Import Templates does not show: samples, expected results and scripts in `.tooling/`, and withdrawn drafts in `.drafts/{vendor}/` as `*.policy.draft` files.
- Drafts are not checked as policies. A draft may have a `.meta.yaml` sidecar, and the lint checks that any sidecar in `.drafts/` has a matching draft.

## Metadata file

```yaml
title: "Cisco IOS SNMP"
description: "One or two sentences on what the policy checks."
vendor: cisco
os: ios
config_format: ios-running-config
collection_command: "show running-config"
kind: hardening
min_rconfig_version: 8.0.2
status: lab-tested
framework_claim: null
notes: "Optional; required when status is under-review."
rules:
  - description: "No SNMPv1 or SNMPv2c community is configured (line snmp-server community is absent)"
    references:
      nist_800_53: ["SC-12"]
      hipaa: ["164.312(e)(1)"]
  - description: "An SNMPv3 user with auth and priv is configured (snmp-server user ... v3 auth ... priv ...)"
    references: {}
```

| Field | Values |
|---|---|
| `config_format` | `ios-running-config`, `junos-display-set`, `junos-brace`, `fortios-full-config`, `routeros-export`, `bigip-scf` |
| `collection_command` | The command rConfig runs to collect the config, or `null` if rConfig has none |
| `kind` | `hardening`, `operational` or `template` |
| `min_rconfig_version` | At least the release that introduced every method the policy uses (see `min_version` in `.tooling/scripts/methods.json`); the lint checks this |
| `status` | `lab-tested`: expected results recorded against at least one `lab` or `sanitised-real` sample. `synthetic-tested`: against `synthetic` samples only. `under-review`: known problems, explained in `notes` |
| `framework_claim` | `null`, or the framework the file names, its label and ID scheme as written, and `ids_local: true` when the IDs are the author's own numbering rather than the published standard's |
| `rules` | Hardening files: one entry per rule, in file order, with the rule's `description` and its published `references`: `nist_800_53` (NIST SP 800-53 control), `hipaa` (45 CFR section), `nist_csf` (NIST CSF 1.1 subcategory). Use `references: {}` when there is none. Do not record local or invented IDs |

## Sample configs

List each sample in `.tooling/samples/{vendor}/samples.yaml` with `file`, `name`, `os`, `os_version`, `config_format`, `source` (`sanitised-real`, `lab` or `synthetic`) and `hardened` (`true` or `false`).

Sanitise every sample before you add it:

- IPv4 addresses from RFC 5737 only (192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24) and IPv6 from RFC 3849 (2001:db8::/32). Netmasks and wildcard masks can stay.
- Host and domain names under `example.com` or `example.net`.
- Fake passwords, hashes, keys and SNMP communities.
- No customer or organisation names, no personal names, and no serial numbers.

## Running the checks

The lint needs Python 3.9 or later and PyYAML, and does not need rConfig Pro:

```bash
pip install pyyaml
python3 .tooling/scripts/lint.py
python3 .tooling/scripts/test_lint.py
```

The lint also runs in GitHub Actions on every push and pull request.

Verification runs every policy against every sample with a matching `config_format`, using rConfig Pro's own parser and evaluator, and compares the results with `.tooling/expected/`. It needs a local rConfig V8 Pro checkout with its Composer dependencies installed. Pro is used read-only.

```bash
# compare with .tooling/expected/ and exit non-zero on any difference
RCONFIG_PRO_PATH=../rconfig8 php .tooling/scripts/verify_with_pro.php

# after adding or changing a policy or sample: rewrite .tooling/expected/, then review the diff
RCONFIG_PRO_PATH=../rconfig8 php .tooling/scripts/verify_with_pro.php --update

# list rules with the same result on every sample, which are untested or broken
RCONFIG_PRO_PATH=../rconfig8 php .tooling/scripts/verify_with_pro.php --uniform
```

When rConfig Pro adds a method, regenerate the method list with `python3 .tooling/scripts/generate_methods.py ../rconfig8`, and add the method's first release to `FIRST_RELEASE` in that script.

## Submitting

Fork the repository, create a branch, commit your changes and open a pull request with a short description of the policy and the devices it was tested on.

If you prefer not to use GitHub, email your policy to `info@rconfig.com` with the vendor and device details, the compliance standard addressed, a short description and your contact details.
