import random
from flask import Flask, jsonify, render_template

app = Flask(__name__)

PREFIXES = ["Lil", "Young", "MC", "Big", "Dr.", "Slim", "Kid", "Baby"]
WORDS = ["Cipher", "Static", "Midnight", "Vandal", "Ghost", "Chrome",
         "Velvet", "Thunder", "Atlas", "Neon", "Riot", "Phantom"]
SUFFIXES = ["the Great", "Da Kid", "XL", "Jr.", "the Poet", "Gold"]


def build_name():
    pattern = random.choice([1, 2, 3])
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
    return jsonify(name=build_name())


if __name__ == "__main__":
    app.run(debug=True)
