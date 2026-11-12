# Clave Segura

Generador de contraseñas en español, construido con FastAPI. Permite elegir la longitud (4–128), los tipos de carácter (mayúsculas, minúsculas, números y símbolos) y evitar caracteres parecidos. Cada contraseña se genera con el módulo `secrets` de Python, incluye al menos un carácter de cada tipo elegido y muestra su entropía y nivel de fuerza.

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

## API

`POST /api/generate`

```json
{
  "length": 16,
  "lowercase": true,
  "uppercase": true,
  "digits": true,
  "symbols": true,
  "exclude_ambiguous": false,
  "count": 1
}
```

Todos los campos son opcionales. `count` admite de 1 a 10 contraseñas por solicitud.

## Pruebas

```powershell
python -m pip install pytest httpx
python -m pytest
```
