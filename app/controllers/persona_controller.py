from typing import List
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from app.utils import faker_utils
from sqlalchemy import text
from ..database import get_db
from ..views.persona import PersonaCreate, PersonaUpdate, PersonaRead, PoblarRequest
from ..services import persona_service

router = APIRouter(prefix="/personas", tags=["personas"])


@router.post("", response_model=PersonaRead, status_code=status.HTTP_201_CREATED)
def create_persona(persona_in: PersonaCreate, db: Session = Depends(get_db)):
    """Create a new Persona delegating to service layer."""
    # Let domain errors bubble up to global handlers
    return persona_service.create_persona(db, persona_in)


@router.get("", response_model=List[PersonaRead])
def list_personas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """List Personas with pagination via service layer."""
    return persona_service.list_personas(db, skip=skip, limit=limit)


@router.get("/{persona_id}", response_model=PersonaRead)
def get_persona(persona_id: int, db: Session = Depends(get_db)):
    """Retrieve a Persona by ID via service layer."""
    return persona_service.get_persona(db, persona_id)


@router.put("/{persona_id}", response_model=PersonaRead)
def update_persona(persona_id: int, persona_in: PersonaUpdate, db: Session = Depends(get_db)):
    """Update an existing Persona (partial) via service layer."""
    return persona_service.update_persona(db, persona_id, persona_in)

# orden e implementación completos reset bd

@router.delete("/reset")
async def reset_personas_endpoint(db: Session = Depends(get_db)):
    result = db.execute(text("DELETE FROM personas"))
    deleted_count = result.rowcount
    db.commit()
    return {
        "message": "Base de datos limpiada. Se eliminaron todos los registros.",
        "deletedcount": deleted_count
    }

@router.delete("/{persona_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_persona(persona_id: int, db: Session = Depends(get_db)):
    """Delete a Persona by ID via service layer."""
    persona_service.delete_persona(db, persona_id)
    return None


@router.delete("/{persona_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_persona(persona_id: int, db: Session = Depends(get_db)):
    """Delete a Persona by ID via service layer."""
    persona_service.delete_persona(db, persona_id)
    return None

# NUEVO ENDPOINT 1: POBLAR MASIVO
@router.post("/poblar", status_code=201)
async def poblar_personas_endpoint(request: PoblarRequest, db: Session = Depends(get_db)):
    try:
        personas_data = faker_utils.generar_personas(request.cantidad)

        # 1. Crear tabla si no existe
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS personas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(80) NOT NULL,
                last_name VARCHAR(80) NOT NULL,
                email VARCHAR(80) NOT NULL,
                phone VARCHAR(50) NOT NULL,
                birth_date DATE NOT NULL,
                is_active TINYINT(1) NOT NULL,
                notes TEXT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """))

        # 2. Insertar los datos generados
        db.execute(
            text("""
                INSERT INTO personas 
                (first_name, last_name, email, phone, birth_date, is_active, notes)
                VALUES (:firstname, :lastname, :email, :phone, :birthdate, :isactive, :notes)
            """),
            personas_data
        )
        db.commit()

        return {"message": f"{request.cantidad} usuarios creados exitosamente", "status": 201}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

