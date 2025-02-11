from sqlalchemy.orm import Session
from models.DataModels import Prediction, TaxonomyField, Document, FieldLabel
from datetime import datetime, UTC
from typing import List, Optional, Dict
import os
import shutil

def upload_document(
    db: Session,
    organization_id: int,
    file_path: str,
    individual_id: str,
    name: Optional[str] = None
) -> Document:
    """
    Upload a document for an organization.
    
    Args:
        db (Session): Database session
        organization_id (int): ID of the organization this document belongs to
        file_path (str): Path to the source document file
        individual_id (str): Unique identifier for the individual associated with document
        name (Optional[str]): Name for the document, defaults to filename if not provided
        
    Returns:
        Document: Created document object
    """
    if name is None:
        name = os.path.basename(file_path)
        
    # Copy file to storage location
    storage_path = f"storage/org_{organization_id}/{name}"
    os.makedirs(os.path.dirname(storage_path), exist_ok=True)
    shutil.copy2(file_path, storage_path)
    
    document = Document(
        name=name,
        file_path=storage_path,
        individual_id=individual_id,
        organization_id=organization_id
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def upload_documents_from_folder(db: Session, folder_path: str, organization_id: int):
    """Process all documents in a folder"""

    for file_name in os.listdir(folder_path):
        if file_name.endswith(('.pdf', '.jpg', '.png', '.txt')):
            file_path = os.path.join(folder_path, file_name)

            # Upload document to our system
            upload_document(
                db=db,
                organization_id=organization_id,
                file_path=file_path,
                individual_id="default",  # You might want to specify this based on your needs
                name=file_name
            )


def get_document(db: Session, document_id: int) -> Optional[Document]:
    """
    Get a document by ID.
    
    Args:
        db (Session): Database session
        document_id (int): ID of the document to retrieve
        
    Returns:
        Optional[Document]: Document object if found, None otherwise
    """
    return db.query(Document).filter(Document.id == document_id).first()

def get_documents(
    db: Session,
    organization_id: Optional[int] = None,
    individual_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Document]:
    """
    Get a list of documents with optional filtering.
    
    Args:
        db (Session): Database session
        organization_id (Optional[int]): Filter documents by organization ID
        individual_id (Optional[str]): Filter documents by individual ID
        skip (int): Number of records to skip
        limit (int): Maximum number of records to return
        
    Returns:
        List[Document]: List of document objects
    """
    query = db.query(Document)
    if organization_id:
        query = query.filter(Document.organization_id == organization_id)
    if individual_id:
        query = query.filter(Document.individual_id == individual_id)
    return query.offset(skip).limit(limit).all()

def update_document(
    db: Session,
    document_id: int,
    name: Optional[str] = None,
    individual_id: Optional[str] = None
) -> Optional[Document]:
    """
    Update a document's details.
    
    Args:
        db (Session): Database session
        document_id (int): ID of the document to update
        name (Optional[str]): New name for the document
        individual_id (Optional[str]): New individual ID for the document
        
    Returns:
        Optional[Document]: Updated document object if found, None otherwise
    """
    document = get_document(db, document_id)
    if document:
        if name is not None:
            document.name = name
        if individual_id is not None:
            document.individual_id = individual_id
        db.commit()
        db.refresh(document)
    return document

def delete_document(db: Session, document_id: int) -> bool:
    """
    Delete a document and its associated file.
    
    Args:
        db (Session): Database session
        document_id (int): ID of the document to delete
        
    Returns:
        bool: True if document was deleted, False if not found
    """
    document = get_document(db, document_id)
    if document:
        # Delete physical file
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        db.delete(document)
        db.commit()
        return True
    return False

def assign_labels(
    db: Session,
    document_id: int,
    taxonomy_id: int,
    labels: Dict[str, str]
) -> bool:
    """
    Assign labels to a document according to a taxonomy.
    
    Args:
        db (Session): Database session
        document_id (int): ID of the document to label
        taxonomy_id (int): ID of the taxonomy to use
        labels (Dict[str, str]): Dictionary mapping field names to label values
        
    Returns:
        bool: True if labels were successfully assigned, False otherwise
        
    Raises:
        ValueError: If required fields are missing from labels
    """
    document = get_document(db, document_id)
    if not document:
        return False
        
    # Get all required fields for the taxonomy
    required_fields = db.query(TaxonomyField).filter(
        TaxonomyField.taxonomy_id == taxonomy_id,
        TaxonomyField.is_required == True
    ).all()
    
    # Verify all required fields are present
    required_field_names = {field.name for field in required_fields}
    provided_field_names = set(labels.keys())
    missing_fields = required_field_names - provided_field_names
    
    if missing_fields:
        raise ValueError(f"Missing required fields: {missing_fields}")
    
    # Remove existing labels
    db.query(FieldLabel).filter(FieldLabel.document_id == document_id).delete()
    
    # Create new labels
    for field_name, value in labels.items():
        field = db.query(TaxonomyField).filter(
            TaxonomyField.taxonomy_id == taxonomy_id,
            TaxonomyField.name == field_name
        ).first()
        
        if field:
            label = FieldLabel(
                document_id=document_id,
                field_id=field.id,
                field_name=field.name,
                value=value
            )
            db.add(label)
    
    document.taxonomy_id = taxonomy_id
    document.is_labeled = True
    db.commit()
    return True




def assign_extraction_values(
    db: Session,
    document_id: int,
    taxonomy_id: int,
    model_id: int,
    extraction_values: Dict[str, str]
) -> bool:
    """
    Assign extraction values to a document from a specific model extraction.
    
    Args:
        db (Session): Database session
        document_id (int): ID of the document to label
        taxonomy_id (int): ID of the taxonomy to use
        extraction_values (Dict[str, str]): Dictionary mapping field names to extraction values
        
    Returns:
        bool: True if extraction values were successfully assigned, False otherwise
        
    Raises:
        ValueError: If required fields are missing from extraction values
    """
    document = get_document(db, document_id)
    if not document:
        return False
        
    # Get all required fields for the taxonomy
    required_fields = db.query(TaxonomyField).filter(
        TaxonomyField.taxonomy_id == taxonomy_id,
        TaxonomyField.is_required == True
    ).all()
    
    # Verify all required fields are present
    required_field_names = {field.name for field in required_fields}
    provided_field_names = set(extraction_values.keys())
    missing_fields = required_field_names - provided_field_names
    
    if missing_fields:
        raise ValueError(f"Missing required fields: {missing_fields}")
    
    # Remove existing extraction values
    db.query(Prediction).filter(Prediction.document_id == document_id,
                                Prediction.model_id == model_id).delete()
    
    # Create new extraction values
    for field_name, value in extraction_values.items():
        field = db.query(TaxonomyField).filter(
            TaxonomyField.taxonomy_id == taxonomy_id,
            TaxonomyField.name == field_name
        ).first()
        
        if field:
            extraction_value = Prediction(
                document_id=document_id,
                field_id=field.id,
                field_name=field.name,
                value=value,
                occurrence=1
            )
            db.add(extraction_value)
    
    document.taxonomy_id = taxonomy_id
    document.is_labeled = True
    db.commit()
    return True




