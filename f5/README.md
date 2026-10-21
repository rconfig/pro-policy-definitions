# F5 Policy Templates

Policy definitions for F5 BIG-IP.

## Expected config format

tmsh configuration in brace format, for example:

```
ltm virtual /Common/vs_app {
    destination /Common/10.1.1.10:443
    profiles {
        /Common/clientssl { }
    }
}
```

The `scope:` anchors (`^ltm virtual`, `^ltm profile client-ssl`, `^ltm pool`, `^sys sshd`, `^sys syslog`) must match top-level object lines, and each object's braces must be balanced.

## Available Policies

| File | Purpose | Rules | Minimum rConfig |
|---|---|---|---|
| `bigip-security-baseline.policy` | F5 BigIP Security Baseline: NTP, syslog and SNMP present, no public or private SNMP communities, SSH idle timeout, remote syslog, WAF logging profiles on WAF-enabled virtual servers, and a WAF policy on externally reachable virtual servers. | 7 | V8.3.0 |
| `bigip-ssl-virtual-hardening.policy` | F5 BigIP SSL/TLS and Virtual Server Hardening: client-SSL profiles disable SSLv3, TLS 1.0 and TLS 1.1 and avoid DEFAULT/ALL ciphers; every pool has a monitor; HTTPS virtual servers use a client-SSL profile and keep source address translation. | 5 | V8.3.0 |

Both files use the `evaluate_block` method (nested any/all/not with per-block scoping). It is available from rConfig V8.3.0; earlier releases do not support it and skip these rules.

## Supported Models

Not stated by the policy authors.

## Implementation Notes

- The TLS 1.0 check uses `regex: '/no-tlsv1(\s|$)/m'` so that `no-tlsv1.1`, `no-tlsv1.2` and `no-tlsv1.3` do not satisfy it. TLS 1.1 is checked separately with `no-tlsv1.1`.
- A scoped rule fails when no config block matches its scope. A config with no client-SSL profiles or pools therefore fails those rules.
