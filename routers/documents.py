from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from app.services.nucleus_client import upload_document_to_nucleus, run_extraction_workflow, fetch_extraction_results

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/", response_model=schemas.DocumentOut)
def create_document(doc_in: schemas.DocumentCreate, db: Session = Depends(get_db)):
    doc = models.Document(
        document_type_id=doc_in.document_type_id,
        nucleus_doc_id=doc_in.nucleus_doc_id,
        status="uploaded"
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

@router.post("/{document_id}/upload_to_nucleus")
def upload_doc_to_nucleus(document_id: int, file_path: str, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter_by(id=document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    nucleus_doc_id = upload_document_to_nucleus(file_path)
    doc.nucleus_doc_id = nucleus_doc_id
    doc.status = "uploaded_to_nucleus"
    db.commit()
    db.refresh(doc)
    return {"message": "Document uploaded to Nucleus", "nucleus_doc_id": nucleus_doc_id}

@router.post("/{document_id}/run_extraction")
def run_extraction(document_id: int, workflow_id: str, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter_by(id=document_id).first()
    if not doc or not doc.nucleus_doc_id:
        raise HTTPException(status_code=404, detail="Document not found or not uploaded to Nucleus")

    result = run_extraction_workflow(doc.nucleus_doc_id, workflow_id)
    # Suppose result has a job_id
    job_id = result.get("job_id")
    return {"message": "Extraction started", "job_id": job_id}

@router.get("/{document_id}/fetch_results")
def fetch_results(document_id: int, job_id: str, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter_by(id=document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    extraction_data = fetch_extraction_results(job_id)
    # Map extraction_data to ExtractionResult model
    # This is highly dependent on how Nucleus returns data
    for item in extraction_data.get("fields", []):
        # e.g., item might have "field_name" and "value"
        taxonomy_field = db.query(models.TaxonomyField).filter_by(
            document_type_id=doc.document_type_id,
            field_name=item["field_name"]
        ).first()
        if taxonomy_field:
            new_result = models.ExtractionResult(
                document_id=doc.id,
                taxonomy_field_id=taxonomy_field.id,
                extracted_value=item.get("value"),
                confidence=item.get("confidence", None),
            )
            db.add(new_result)
    doc.status = "extracted"
    db.commit()
    db.refresh(doc)
    return {"message": "Extraction results fetched and stored"}
