import random
import re
from flask import Flask, jsonify, render_template, request
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["60 per minute"],
    storage_uri="memory://",
)

Talisman(
    app,
    content_security_policy={
        "default-src": "'self'",
        "style-src": "'self'",
        "script-src": "'self'",
    },
    force_https=False,
)
PREFIXES = ["Lil", "Young", "MC", "Big", "Dr.", "Slim", "Kid", "Baby"]
WORDS = ["Cipher", "Static", "Midnight", "Vandal", "Ghost", "Chrome",
         "Velvet", "Thunder", "Atlas", "Neon", "Riot", "Phantom"]
SUFFIXES = ["the Great", "Da Kid", "XL", "Jr.", "the Poet", "Gold"]

# Allowlist: letters, numbers, spaces, hyphens, apostrophes. 1-20 characters.
SEED_PATTERN = re.compile(r"^[A-Za-z0-9 '\-]{1,20}$")
MAX_RAW_LENGTH = 100


def clean_seed(raw):
    """Return a safe seed string, or None if the input is not allowed."""
    if len(raw) > MAX_RAW_LENGTH:
        return None
    seed = " ".join(raw.split())  # trim and collapse extra whitespace
    if not SEED_PATTERN.fullmatch(seed):
        return None
    return seed


def build_name(seed=None):
    pattern = random.choice([1, 2, 3])
    if seed:
        if pattern == 1:
            return f"{random.choice(PREFIXES)} {seed}"
        if pattern == 2:
            return f"{seed} {random.choice(SUFFIXES)}"
        return f"{random.choice(PREFIXES)} {seed} {random.choice(SUFFIXES)}"
    if pattern == 1:
        return f"{random.choice(PREFIXES)} {random.choice(WORDS)}"
    if pattern == 2:
        return f"{random.choice(WORDS)} {random.choice(SUFFIXES)}"
    return f"{random.choice(PREFIXES)} {random.choice(WORDS)} {random.choice(SUFFIXES)}"


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/generate")
@limiter.limit("10 per minute")
def generate():
    raw = request.args.get("seed", "")
    if raw.strip() == "":
        return jsonify(name=build_name())
    seed = clean_seed(raw)
    if seed is None:
        return jsonify(
            error="Use 1-20 letters, numbers, spaces, hyphens, or apostrophes."
        ), 400
    return jsonify(name=build_name(seed))


@app.errorhandler(429)
def too_many_requests(e):
    return jsonify(error="Too many requests. Please wait a minute."), 429

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")