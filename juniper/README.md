# Juniper Policy Templates

Policy definitions for Juniper Junos devices.

These policies are withdrawn while they are updated for `display set` format, and do not appear in Import Templates.

## Expected config format

These rules are written for Junos **brace (hierarchical) format**, as returned by `show configuration`:

```
system {
    services {
        ssh;
    }
}
```

They do not match `show configuration | display set` output. rConfig's Junos demo platform collects `show configuration | display set`. On a device collected that way, the brace-format rules (`match_code_block_flexible`, `match_code_block_from_array`) fail, and the `must_not_match_regex` rules always pass. Assign these policies to a command that returns brace format, or use set-format rules.

## Available Policies

| File | Framework | Purpose | Rules | Minimum rConfig |
|---|---|---|---|---|
| `juniper_junos_base.policy` | None (generic hardening) | rConfig Base Coverage for JunOS (generic hardening), version 1.0. | 9 | V8.0.2 |
| `juniper_junos_CIS_benchmark.policy` | CIS-style | CIS JunOS-style Baseline (modeled after CIS IOS coverage), version 1.0. | 11 | V8.0.2 |
| `juniper_junos_HIPAA_benchmark.policy` | HIPAA | HIPAA Technical Safeguards mapped to JunOS, version 1.0. | 8 | V8.0.2 |
| `juniper_junos_ISO27K_benchmark.policy` | ISO/IEC 27001 / 27002 Annex A | ISO/IEC 27001/27002 Annex A mapped to JunOS, version 1.0. | 7 | V8.0.2 |
| `juniper_junos_JUNIPERSAFE_benchmark.policy` | Cisco SAFE (adapted) | Cisco SAFE-aligned Baseline adapted for Juniper JunOS, version 1.0. | 13 | V8.0.2 |
| `juniper_junos_NIST_benchmark.policy` | NIST SP 800-53 | NIST SP 800-53 Technical Controls mapped to JunOS, version 1.0. | 8 | V8.0.2 |
| `juniper_junos_NISTCSF_benchmark.policy` | NIST CSF | NIST Cybersecurity Framework mapped to JunOS, version 1.0. | 6 | V8.0.2 |
| `juniper_junos_PCIDSS_benchmark.policy` | PCI DSS | PCI DSS mapped to JunOS, version 1.0. | 7 | V8.0.2 |

The minimum version comes from the methods each file uses: `must_not_match_regex` needs V8.0.2 or later.

## Supported Models

Not stated by the policy authors.

## Implementation Notes

- Control IDs are rConfig's own numbering. The CIS file is modeled after CIS IOS coverage, not a published CIS Junos benchmark.
- The `must_not_match_regex` rules match a minimal brace structure such as `system { services { telnet; } }`. They only detect the setting when it is the sole child of that block.
