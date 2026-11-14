# Rap Name Generator

A Flask web app that generates hip-hop and rap names for aspiring artists who need inspiration for a pen name.

## Features
- One-click name generation
- Optional seed word worked into the name
- Server-side input validation (allowlist)

## Run locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000

## Roadmap
- [x] Phase 1: basic generator
- [x] Phase 2a: seed input with validation
- [ ] Phase 2b: rate limiting, security headers
- [ ] Phase 3: accounts and favorites using MFA login
- [ ] Phase 4: tests, CI security scanning, threat model
- [ ] Phase 5: deployment