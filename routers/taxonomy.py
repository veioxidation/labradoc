from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/taxonomy", tags=["taxonomy"])

@router.post("/", response_model=schemas.TaxonomyFieldOut)
def create_taxonomy_field(taxonomy_in: schemas.TaxonomyFieldCreate, db: Session = Depends(get_db)):
    doc_type = db.query(models.DocumentType).filter_by(id=taxonomy_in.document_type_id).first()
    if not doc_type:
        raise HTTPException(status_code=404, detail="DocumentType not found")

    field = models.TaxonomyField(
        document_type_id=taxonomy_in.document_type_id,
        field_name=taxonomy_in.field_name,
        data_type=taxonomy_in.data_type,
        is_required=taxonomy_in.is_required,
        validation_rules=taxonomy_in.validation_rules
    )
    db.add(field)
    db.commit()
    db.refresh(field)
    return field

@router.get("/{taxonomy_id}", response_model=schemas.TaxonomyFieldOut)
def get_taxonomy_field(taxonomy_id: int, db: Session = Depends(get_db)):
    field = db.query(models.TaxonomyField).filter_by(id=taxonomy_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    return field
