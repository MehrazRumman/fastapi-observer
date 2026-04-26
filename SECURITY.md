# Security Policy

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 0.1.x   | Yes       |

## Reporting a Vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Instead, report them by emailing **blackndmaroon@gmail.com** with the subject line:

```
[fastapi-inspector] Security vulnerability report
```

Include as much of the following as you can:

- A description of the vulnerability and its potential impact
- The file(s) and line number(s) involved
- A minimal reproducible example or proof-of-concept
- Any suggested fix (optional but appreciated)

You will receive an acknowledgement within **72 hours** and a resolution timeline once the issue is assessed. We follow responsible disclosure — please allow us reasonable time to address the issue before any public disclosure.

## Security Considerations for Users

- **Do not log sensitive fields** (passwords, tokens, PII). Use path or header filters in `ObserverConfig` to exclude them.
- **Restrict access to the dashboard** — mount it behind authentication middleware in production.
- **Secure storage files** — JSON and SQLite storage files contain request data; apply appropriate filesystem permissions.
- Keep your `fastapi` and `pydantic` dependencies up to date to pick up upstream security fixes.
