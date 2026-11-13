import random
import re
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

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


if __name__ == "__main__":
    app.run(debug=True)