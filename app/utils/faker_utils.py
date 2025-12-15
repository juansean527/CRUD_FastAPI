import random
import unicodedata
from faker import Faker
from typing import List, Dict, Any

fake = Faker('es_ES')
DOMINIOS_REALES = ['gmail.com', 'hotmail.com', 'outlook.com', 'yahoo.com']

def normalizar(texto: str) -> str:
    # quitar acentos y pasar a ascii simple
    nfkd = unicodedata.normalize("NFKD", texto)
    solo_ascii = "".join(c for c in nfkd if not unicodedata.combining(c))
    # quitar espacios y pasar a minúsculas
    return solo_ascii.replace(" ", "").lower()

def generar_personas(cantidad: int) -> List[Dict[str, Any]]:
    """Genera personas para inserción masiva."""
    if cantidad <= 0 or cantidad >= 1000:
        raise ValueError("Cantidad debe estar entre 1 y 999")
    
    personas = []
    for _ in range(cantidad):
        firstname = fake.first_name()
        lastname = fake.last_name()
        dominio = random.choice(DOMINIOS_REALES)

        user = f"{normalizar(firstname)}.{normalizar(lastname)}"
        email = f"{user}@{dominio}"
        personas.append({
            "firstname": firstname,
            "lastname": lastname,
            "email": email,
            "phone": fake.phone_number()[:15],
            "birthdate": fake.date_of_birth(minimum_age=18, maximum_age=80).strftime('%Y-%m-%d'),
            "isactive": random.choice([True, False]),
            "notes": fake.sentence(nb_words=6) if random.random() > 0.2 else None
        })
    return personas