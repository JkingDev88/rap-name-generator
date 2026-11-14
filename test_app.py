import pytest

from app import app, limiter


@pytest.fixture
def client():
    app.config["TESTING"] = True
    limiter.reset()  # start every test with a clean rate-limit counter
    with app.test_client() as client:
        yield client


# --- Pages and static files -------------------------------------------------

def test_home_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Rap Name Generator" in response.data


def test_page_has_no_inline_script_or_style(client):
    # The CSP only allows 'self', so inline code would be blocked in browsers.
    html = client.get("/").get_data(as_text=True)
    assert "<script>" not in html
    assert "<style>" not in html


def test_static_files_are_served(client):
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/static/style.css").status_code == 200


# --- Security headers --------------------------------------------------------

def test_security_headers_present(client):
    response = client.get("/")
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert "X-Frame-Options" in response.headers
    assert "Referrer-Policy" in response.headers


# --- Name generation ---------------------------------------------------------

def test_blank_seed_returns_a_name(client):
    response = client.get("/generate")
    assert response.status_code == 200
    assert response.get_json()["name"]


def test_valid_seed_is_used_in_the_name(client):
    response = client.get("/generate?seed=Jet")
    assert response.status_code == 200
    assert "Jet" in response.get_json()["name"]


# --- Input validation --------------------------------------------------------

@pytest.mark.parametrize("bad_seed", [
    "<script>",
    "<b>",
    "a;b",
    "x" * 21,    # one over the 20-character limit
    "x" * 200,   # over the raw-length cap
])
def test_invalid_seeds_are_rejected(client, bad_seed):
    response = client.get("/generate", query_string={"seed": bad_seed})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_seed_at_the_length_limit_is_accepted(client):
    response = client.get("/generate", query_string={"seed": "x" * 20})
    assert response.status_code == 200


# --- Rate limiting -----------------------------------------------------------

def test_rate_limit_blocks_the_eleventh_request(client):
    for _ in range(10):
        assert client.get("/generate?seed=test").status_code == 200
    response = client.get("/generate?seed=test")
    assert response.status_code == 429
    assert "error" in response.get_json()