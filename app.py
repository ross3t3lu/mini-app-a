from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parent

QUESTIONS = [
    {
        "id": 1,
        "category": "Ciencia",
        "question": "¿Qué planeta del sistema solar tiene más lunas confirmadas?",
        "options": ["Júpiter", "Saturno", "Neptuno", "Urano"],
        "answer": 1,
        "explanation": "Saturno encabeza la lista con más de 140 lunas confirmadas.",
        "difficulty": "Fácil",
    },
    {
        "id": 2,
        "category": "Ciencia",
        "question": "¿Cuál es el símbolo químico del oro?",
        "options": ["Ag", "Fe", "Au", "O"],
        "answer": 2,
        "explanation": "Au viene del latín aurum, que significa oro.",
        "difficulty": "Fácil",
    },
    {
        "id": 3,
        "category": "Ciencia",
        "question": "¿Qué tipo de célula no tiene núcleo?",
        "options": ["Neurona", "Célula vegetal", "Célula procariota", "Glóbulo blanco"],
        "answer": 2,
        "explanation": "Las procariotas, como las bacterias, no tienen un núcleo delimitado.",
        "difficulty": "Media",
    },
    {
        "id": 4,
        "category": "Historia",
        "question": "¿En qué año llegó el ser humano a la Luna por primera vez?",
        "options": ["1965", "1969", "1972", "1959"],
        "answer": 1,
        "explanation": "La misión Apolo 11 alunizó el 20 de julio de 1969.",
        "difficulty": "Fácil",
    },
    {
        "id": 5,
        "category": "Historia",
        "question": "¿Cuál fue la capital del Imperio inca?",
        "options": ["Lima", "Quito", "Cusco", "La Paz"],
        "answer": 2,
        "explanation": "Cusco, en el actual Perú, fue el centro político del Imperio inca.",
        "difficulty": "Fácil",
    },
    {
        "id": 6,
        "category": "Historia",
        "question": "¿Qué civilización construyó la ciudad de Petra?",
        "options": ["Los nabateos", "Los fenicios", "Los persas", "Los hititas"],
        "answer": 0,
        "explanation": "Los nabateos tallaron Petra en la roca hace más de dos mil años.",
        "difficulty": "Media",
    },
    {
        "id": 7,
        "category": "Naturaleza",
        "question": "¿Cuál es el animal terrestre más rápido?",
        "options": ["León", "Guepardo", "Antílope", "Avestruz"],
        "answer": 1,
        "explanation": "El guepardo puede alcanzar cerca de 100 km/h en distancias cortas.",
        "difficulty": "Fácil",
    },
    {
        "id": 8,
        "category": "Naturaleza",
        "question": "¿Cuál es el océano más grande del planeta?",
        "options": ["Atlántico", "Índico", "Ártico", "Pacífico"],
        "answer": 3,
        "explanation": "El océano Pacífico cubre aproximadamente un tercio de la superficie terrestre.",
        "difficulty": "Fácil",
    },
    {
        "id": 9,
        "category": "Naturaleza",
        "question": "¿Cómo se llama el proceso por el que las plantas producen su alimento?",
        "options": ["Fermentación", "Fotosíntesis", "Respiración", "Polinización"],
        "answer": 1,
        "explanation": "Durante la fotosíntesis, las plantas usan luz, agua y dióxido de carbono.",
        "difficulty": "Fácil",
    },
    {
        "id": 10,
        "category": "Cultura pop",
        "question": "¿En qué saga aparece el personaje de Frodo Bolsón?",
        "options": ["Harry Potter", "Las crónicas de Narnia", "El señor de los anillos", "Dune"],
        "answer": 2,
        "explanation": "Frodo es el hobbit protagonista de El señor de los anillos.",
        "difficulty": "Fácil",
    },
    {
        "id": 11,
        "category": "Cultura pop",
        "question": "¿Qué instrumento toca Lisa Simpson?",
        "options": ["Piano", "Saxofón", "Batería", "Trompeta"],
        "answer": 1,
        "explanation": "Lisa es conocida por tocar el saxofón barítono.",
        "difficulty": "Fácil",
    },
    {
        "id": 12,
        "category": "Cultura pop",
        "question": "¿Cuál fue el primer largometraje de Pixar?",
        "options": ["Bichos", "Toy Story", "Monsters, Inc.", "Buscando a Nemo"],
        "answer": 1,
        "explanation": "Toy Story, estrenada en 1995, fue el primer largometraje de Pixar.",
        "difficulty": "Media",
    },
]

CATEGORY_DETAILS = {
    "Ciencia": {"icon": "✳", "color": "violet", "description": "Ideas que mueven el mundo"},
    "Historia": {"icon": "◷", "color": "orange", "description": "Viaja a través del tiempo"},
    "Naturaleza": {"icon": "❋", "color": "green", "description": "Descubre nuestro planeta"},
    "Cultura pop": {"icon": "♫", "color": "pink", "description": "Películas, series y más"},
}


class PublicQuestion(BaseModel):
    id: int
    category: str
    question: str
    options: list[str]
    difficulty: str


class AnswerSubmission(BaseModel):
    question_id: int
    option_index: Annotated[int, Field(ge=0, le=3)]


class AnswerResult(BaseModel):
    correct: bool
    correct_index: int
    explanation: str


app = FastAPI(title="Trivia Club", description="Una trivia rápida para mentes curiosas.")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/api/categories")
def get_categories() -> list[dict[str, str | int]]:
    return [
        {
            "name": name,
            "icon": details["icon"],
            "color": details["color"],
            "description": details["description"],
            "question_count": sum(question["category"] == name for question in QUESTIONS),
        }
        for name, details in CATEGORY_DETAILS.items()
    ]


@app.get("/api/questions", response_model=list[PublicQuestion])
def get_questions(
    category: str | None = None,
    limit: Annotated[int, Query(ge=1, le=20)] = 10,
) -> list[PublicQuestion]:
    questions = QUESTIONS
    if category is not None:
        if category not in CATEGORY_DETAILS:
            raise HTTPException(status_code=404, detail="No encontramos esa categoría.")
        questions = [question for question in QUESTIONS if question["category"] == category]
    return [PublicQuestion.model_validate(question) for question in questions[:limit]]


@app.post("/api/answer", response_model=AnswerResult)
def submit_answer(submission: AnswerSubmission) -> AnswerResult:
    question = next(
        (item for item in QUESTIONS if item["id"] == submission.question_id),
        None,
    )
    if question is None:
        raise HTTPException(status_code=404, detail="No encontramos esa pregunta.")
    correct_index = question["answer"]
    return AnswerResult(
        correct=submission.option_index == correct_index,
        correct_index=correct_index,
        explanation=question["explanation"],
    )
