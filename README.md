# Rap Name Generator

A Flask web app that generates hip-hop and rap names for aspiring artists who need inspiration for a pen name.

## Features

- One-click name generation
- Optional seed word worked into the name
- Server-side input validation (allowlist)
- Rate limiting and security headers

## Run locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000

To run with Flask's debugger and auto-reload (local development only):

```bash
FLASK_DEBUG=1 python app.py
```

## Security

| Control | Implementation |
|---|---|
| Input validation | Allowlist regex: 1-20 letters, numbers, spaces, hyphens, or apostrophes. Raw input over 100 characters is rejected before processing. Whitespace is collapsed. Invalid input returns HTTP 400. |
| Rate limiting | Flask-Limiter: 10 requests/minute on `/generate`, 60/minute default per IP. Over the limit returns HTTP 429 with a JSON message. |
| Security headers | Flask-Talisman sets Content-Security-Policy, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, and Permissions-Policy. |
| Content Security Policy | `default-src`, `script-src`, and `style-src` are limited to `'self'`. No inline scripts or styles: JavaScript lives in `static/app.js` and CSS in `static/style.css`. |
| Safe output | Results are written to the page with `textContent`, never `innerHTML`. |
| Debug mode | Off by default. It is only enabled when `FLASK_DEBUG=1` is set. |
| CSRF | Not needed for the current design: `/generate` is a read-only GET that changes no state. This will be revisited in Phase 3 when accounts and POST requests are added. |

## Testing the controls

With the app running, these checks were run against it:

```bash
# Security headers are present
curl -I http://127.0.0.1:5000/

# Invalid input is rejected (expect HTTP 400 and an error message)
curl "http://127.0.0.1:5000/generate?seed=%3Cscript%3E"

# Rate limit triggers (expect 200s, then 429s after the 10th request)
for i in $(seq 1 12); do curl -s -o /dev/null -w "%{http_code}\n" "http://127.0.0.1:5000/generate?seed=test"; done
```

Results: all expected headers were returned, the `<script>` seed was rejected with a 400, and requests past the limit returned 429. Before the inline script and styles were moved into `static/`, Chrome's console showed the CSP blocking both, which confirmed the policy was being enforced.

## Known limitations

- Rate-limit counters are stored in memory, so they reset on restart and are not shared across multiple workers. A production deployment would use Redis or similar.
- Flask's built-in development server is not meant for production. Deployment (Phase 5) will use a production WSGI server.
- HTTPS is not forced locally (`force_https=False`). It should be enabled when deployed.
- The development server reveals its software and version in the `Server` header. A production server setup can suppress this.
- Tests run locally only. CI security scanning is planned for Phase 4.
## Running the tests

```bash
pip install -r requirements-dev.txt
pytest -v
```

The suite (13 tests) covers:

- Pages and static files load, with no inline scripts or styles (required by the CSP)
- Security headers are present on responses
- Name generation works with and without a seed
- Invalid seeds (HTML tags, symbols, over-length input) return 400
- The 11th request within a minute returns 429

## Roadmap

- [x] Phase 1: basic generator
- [x] Phase 2a: seed input with validation
- [x] Phase 2b: rate limiting, security headers
- [ ] Phase 3: accounts and favorites using MFA login
- [ ] Phase 4: tests, CI security scanning, threat model
- [ ] Phase 5: deployment