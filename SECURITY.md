# Security policy

## Reporting a vulnerability

Please report security issues privately through GitHub's private vulnerability reporting: open the
**Security** tab of `github.com/erdem-afk/knotenlinie` and choose **Report a vulnerability**. Do not open a
public issue for a security problem.

Include what you found, how to reproduce it and what it affects. We will acknowledge the report, keep you
informed, and credit you in the fix unless you prefer not to be named.

## Scope

- The code in this repository, in particular the downloaders (network access, TLS, file handling) and anything
  that reads files supplied by a user.
- **The seal gates.** A way to make the code download, open or print earthquake records dated 2021-01-01 or
  later, or to open the 2016–2020 Italian blind window without the documented procedure, is treated as a
  security issue ([docs/SEAL-AND-BLIND-WINDOW.md](docs/SEAL-AND-BLIND-WINDOW.md)).

Third-party data services and Python packages are outside this policy; please report problems with them to their
maintainers.

## Supported versions

Only the latest state of the `main` branch is supported.
