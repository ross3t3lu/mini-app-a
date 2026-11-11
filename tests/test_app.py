from fastapi.testclient import TestClient

from app import app


client = TestClient(app)


def test_homepage_serves_the_trivia_app() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "Trivia Club" in response.text


def test_categories_include_question_counts() -> None:
    response = client.get("/api/categories")

    assert response.status_code == 200
    assert len(response.json()) == 4
    assert all(category["question_count"] == 3 for category in response.json())


def test_question_list_does_not_expose_answers() -> None:
    response = client.get("/api/questions?category=Ciencia")

    assert response.status_code == 200
    assert len(response.json()) == 3
    assert all("answer" not in question for question in response.json())
    assert all("explanation" not in question for question in response.json())


def test_answer_reports_correctness_and_explanation() -> None:
    response = client.post("/api/answer", json={"question_id": 1, "option_index": 1})

    assert response.status_code == 200
    assert response.json() == {
        "correct": True,
        "correct_index": 1,
        "explanation": "Saturno encabeza la lista con más de 140 lunas confirmadas.",
    }


def test_unknown_category_and_question_return_not_found() -> None:
    category_response = client.get("/api/questions?category=Desconocida")
    answer_response = client.post("/api/answer", json={"question_id": 999, "option_index": 0})

    assert category_response.status_code == 404
    assert answer_response.status_code == 404


def test_answer_rejects_an_invalid_option_index() -> None:
    response = client.post("/api/answer", json={"question_id": 1, "option_index": 4})

    assert response.status_code == 422
