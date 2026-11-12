import math
import secrets
import string
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parent

AMBIGUOUS = set("Il1O0o")
SYMBOLS = "!@#$%^&*()-_=+[]{};:,.?/"

CHARACTER_SETS = {
    "lowercase": string.ascii_lowercase,
    "uppercase": string.ascii_uppercase,
    "digits": string.digits,
    "symbols": SYMBOLS,
}

MIN_LENGTH = 4
MAX_LENGTH = 128


class PasswordOptions(BaseModel):
    length: Annotated[int, Field(ge=MIN_LENGTH, le=MAX_LENGTH)] = 16
    lowercase: bool = True
    uppercase: bool = True
    digits: bool = True
    symbols: bool = True
    exclude_ambiguous: bool = False
    count: Annotated[int, Field(ge=1, le=10)] = 1


class GeneratedPassword(BaseModel):
    password: str
    entropy_bits: float
    strength: str


class GenerationResult(BaseModel):
    passwords: list[GeneratedPassword]
    pool_size: int


def build_pools(options: PasswordOptions) -> list[str]:
    pools = []
    for name, characters in CHARACTER_SETS.items():
        if getattr(options, name):
            if options.exclude_ambiguous:
                characters = "".join(c for c in characters if c not in AMBIGUOUS)
            pools.append(characters)
    return pools


def generate_password(length: int, pools: list[str]) -> str:
    """Genera una contraseña con al menos un carácter de cada conjunto elegido."""
    alphabet = "".join(pools)
    characters = [secrets.choice(pool) for pool in pools]
    characters += [secrets.choice(alphabet) for _ in range(length - len(characters))]
    secrets.SystemRandom().shuffle(characters)
    return "".join(characters)


def entropy_bits(length: int, pool_size: int) -> float:
    return round(length * math.log2(pool_size), 1)


def strength_label(bits: float) -> str:
    if bits < 40:
        return "Débil"
    if bits < 60:
        return "Aceptable"
    if bits < 80:
        return "Fuerte"
    return "Muy fuerte"


app = FastAPI(
    title="Clave Segura",
    description="Genera contraseñas aleatorias y seguras al instante.",
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.post("/api/generate", response_model=GenerationResult)
def generate(options: PasswordOptions) -> GenerationResult:
    pools = build_pools(options)
    if not pools:
        raise HTTPException(status_code=400, detail="Elige al menos un tipo de carácter.")
    if options.length < len(pools):
        raise HTTPException(
            status_code=400,
            detail="La longitud debe ser al menos igual a los tipos de carácter elegidos.",
        )
    pool_size = len(set("".join(pools)))
    bits = entropy_bits(options.length, pool_size)
    label = strength_label(bits)
    return GenerationResult(
        passwords=[
            GeneratedPassword(
                password=generate_password(options.length, pools),
                entropy_bits=bits,
                strength=label,
            )
            for _ in range(options.count)
        ],
        pool_size=pool_size,
    )
