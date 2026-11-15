# Threat Model

Rap Name Generator. Last reviewed: 2026-11-14.

This is a lightweight STRIDE-style review. It covers the app as it exists today (Phases 1 to 2) and lists threats to design for in Phase 3 (accounts and MFA login).

## 1. What is being protected

| Asset | Why it matters |
|---|---|
| Availability of the site | A public service that bots can flood or crash |
| Integrity of pages and responses | Visitors must not receive attacker-controlled script or markup |
| The server and its secrets | Debug tooling or leaked config could give an attacker code execution |
| Source code and CI pipeline | A compromised workflow or dependency affects everyone who runs the project |
| User accounts, passwords, MFA codes, favorites (Phase 3) | Not stored yet. Covered in section 5 |

## 2. Entry points and trust boundary

The trust boundary is between the visitor's browser and the Flask app. Everything from the browser is untrusted.

| Entry point | Input | Notes |
|---|---|---|
| GET / | None | Serves the page |
| GET /generate | Query string parameter "seed" | The only user-controlled input |
| GET /static/... | File path | Serves app.js and style.css only |

## 3. Who might attack it

- **Anonymous visitor probing for flaws:** tries script tags, long strings, odd characters in the seed.
- **Automated bots:** scrape, flood, or scan for common vulnerabilities.
- **Supply-chain attacker:** targets a dependency or a CI action instead of the app itself.

There are no logged-in users and no privileged roles today.

## 4. Current threats and mitigations

| # | Threat (STRIDE category) | How it could happen | Mitigation | Status |
|---|---|---|---|---|
| 1 | Cross-site scripting (Tampering) | Seed containing script or HTML is reflected back to the page | Allowlist regex (letters, numbers, spaces, hyphens, apostrophes, 1-20 characters); results rendered with textContent, never innerHTML; CSP limited to self with no inline code | Mitigated |
| 2 | Malformed or oversized input (Tampering, DoS) | Very long or unusual seed values | Raw input capped at 100 characters, cleaned seed at 20; invalid input returns 400 | Mitigated |
| 3 | Request flooding (Denial of service) | Bot hammers /generate | Flask-Limiter: 10 per minute on /generate, 60 per minute default; JSON 429 response | Partial: counters live in memory, reset on restart and are not shared across workers. Limits are per IP, so shared networks share a quota, and behind a proxy the visible IP must be configured correctly |
| 4 | Clickjacking (Tampering) | Site embedded in a hostile page | X-Frame-Options header set by Flask-Talisman | Mitigated |
| 5 | MIME sniffing (Tampering) | Browser guesses a dangerous content type | X-Content-Type-Options: nosniff | Mitigated |
| 6 | Information disclosure | Version details and debug pages help an attacker | Debug mode off unless FLASK_DEBUG=1 (the Werkzeug debugger allows code execution); Referrer-Policy and Permissions-Policy set | Partial: the development server still reveals its software and version in the Server header |
| 7 | Vulnerable dependency (Supply chain) | A package has a known CVE | pip-audit in CI on every push; pinned versions in requirements.txt | Partial: only catches known issues; Python 3.9 is past end of life and should be upgraded |
| 8 | Compromised CI or token (Supply chain, Elevation of privilege) | Malicious or hijacked workflow or credential | Workflow permissions limited to contents: read; runner pinned to ubuntu-24.04; push token is fine-grained, single-repo, and expires | Partial: actions are pinned by major version tag, not commit SHA |
| 9 | Insecure code patterns | Mistakes introduced during development | bandit static scan in CI. Rule B311 (use of random) is skipped on purpose: random is only used to pick words, never for secrets | Mitigated |
| 10 | Eavesdropping or tampering in transit | Traffic read or modified on plain HTTP | HTTPS not forced locally (force_https=False) | Open until deployment (Phase 5) |
| 11 | Repudiation | No record of who did what | No logging yet | Open. Low impact today, needed once accounts exist |
| 12 | Cross-site request forgery | Forged request changes state | Not applicable: the only route is a read-only GET that changes no state | N/A. Revisit when POST routes are added |

## 5. Threats to design for in Phase 3 (accounts and MFA login)

Adding logins turns this into a different kind of application. These are the planned controls.

| Threat | Planned control |
|---|---|
| Password theft from a database leak | Store only salted hashes using a slow algorithm (scrypt, bcrypt, or Argon2); never store or log plaintext |
| Credential stuffing and password guessing | Strict rate limits on the login route; generic error messages; temporary lockout or backoff after repeated failures |
| Account enumeration | Identical responses for "wrong password" and "no such user"; same for password reset |
| MFA code brute force or replay | Random codes from the secrets module (not random); short expiry; single use; limited attempts; rate limiting on the verify route |
| Session hijacking and fixation | Secure, HttpOnly, SameSite cookies; new session ID at login; logout invalidates the session; HTTPS only |
| Cross-site request forgery | CSRF tokens on every state-changing POST (Flask-WTF CSRFProtect) |
| Access to other users' favorites (IDOR) | Check on the server that every record belongs to the logged-in user |
| SQL injection | Parameterized queries or an ORM; never build SQL with string formatting |
| Leaked secrets in the repo | SECRET_KEY and mail credentials come from environment variables, never committed; check history before pushing |
| Mailbox compromise defeating email MFA | Document as a known limitation; consider a TOTP authenticator option later |

## 6. Out of scope

- Network-scale DDoS (needs infrastructure-level protection)
- Compromise of the host operating system or hosting provider
- Physical access to the machine
- Attacks on users' own devices or browsers

## 7. Review

Update this document when a route is added, when Phase 3 lands, and before deployment. Re-check each "Partial" and "Open" row at that point.