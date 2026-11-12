import string

from fastapi.testclient import TestClient

from app import AMBIGUOUS, SYMBOLS, app


client = TestClient(app)


def test_homepage_serves_the_generator() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "Clave Segura" in response.text


def test_default_generation_returns_one_strong_password() -> None:
    response = client.post("/api/generate", json={})

    assert response.status_code == 200
    body = response.json()
    assert len(body["passwords"]) == 1
    result = body["passwords"][0]
    assert len(result["password"]) == 16
    assert result["strength"] == "Muy fuerte"


def test_password_includes_every_selected_character_type() -> None:
    response = client.post("/api/generate", json={"length": 4, "count": 10})

    for result in response.json()["passwords"]:
        password = result["password"]
        assert any(c in string.ascii_lowercase for c in password)
        assert any(c in string.ascii_uppercase for c in password)
        assert any(c in string.digits for c in password)
        assert any(c in SYMBOLS for c in password)


def test_only_digits_when_other_sets_are_disabled() -> None:
    response = client.post(
        "/api/generate",
        json={"length": 12, "lowercase": False, "uppercase": False, "symbols": False},
    )

    body = response.json()
    assert body["passwords"][0]["password"].isdigit()
    assert body["pool_size"] == 10
    assert body["passwords"][0]["strength"] == "Débil"


def test_exclude_ambiguous_characters() -> None:
    response = client.post(
        "/api/generate",
        json={"length": 128, "exclude_ambiguous": True, "count": 5},
    )

    for result in response.json()["passwords"]:
        assert not set(result["password"]) & AMBIGUOUS


def test_rejects_when_no_character_type_is_selected() -> None:
    response = client.post(
        "/api/generate",
        json={"lowercase": False, "uppercase": False, "digits": False, "symbols": False},
    )

    assert response.status_code == 400


def test_rejects_out_of_range_length() -> None:
    assert client.post("/api/generate", json={"length": 3}).status_code == 422
    assert client.post("/api/generate", json={"length": 129}).status_code == 422
