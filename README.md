# Trivia Club

Aplicación web de trivia en español, construida con FastAPI. Incluye cuatro categorías, preguntas de opción múltiple, explicación de las respuestas y un resumen del resultado.

## Requisitos

- Python 3.10 o posterior
- Dependencias de `requirements.txt`

## Ejecutar

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app:app --reload
```

Abre <http://127.0.0.1:8000>. La documentación de la API está disponible en <http://127.0.0.1:8000/docs>.

## Pruebas

```powershell
python -m pip install pytest httpx
python -m pytest
```
