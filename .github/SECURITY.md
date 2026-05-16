# Security Policy

## Supported versions

Only the `main` branch is actively supported.
Older tags do not receive security patches.

## How to report a vulnerability

**Do not open a public issue** - that gives potential attackers
time before a patch ships.

Instead:

1. Open a private
   [Security advisory](https://github.com/Bvitriak/quiz-system/security/advisories/new),
   or
2. Email `bvitriak@gmail.com` with the subject `[SECURITY] quiz-system`.

In your report, include:
- a description of the vulnerability and its potential impact;
- reproduction steps / PoC;
- the branch or commit you tested against;
- a suggested fix, if you have one.

## SLA

| Step | Target                                  |
|-----|-----------------------------------------|
| Acknowledge receipt | within 3 business days                  |
| Initial severity assessment | within 7 business days                  |
| Patch / release | depends on severity, typically ≤ 30 days |

## What is NOT considered a vulnerability

- Behavior of the Flask dev server (`python -m src.main` - not for production).
- A weak DB user password set in `.env.example`.
- Lack of rate limiting (currently out of scope; PRs welcome).

## Known limitations of the current version

- No CSRF protection on POST routes (see [docs/deployment.md](../docs/deployment.md)).
- Session is stored in a signed cookie - the contents are readable by the client.
- `password_hash` uses bcrypt with 12 rounds. This can be raised for production.
