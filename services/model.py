from sqlalchemy.orm import Session
from models.DataModels import ExtractionModel
from datetime import datetime, UTC
from typing import List, Optional

def create_extraction_model(
    db: Session,
    name: str,
    taxonomy_id: int,
    description: Optional[str] = None
) -> ExtractionModel:
    """
    Create a new extraction model.
    
    Args:
        db (Session): Database session
        name (str): Name of the extraction model
        taxonomy_id (int): ID of the taxonomy this model belongs to
        description (Optional[str]): Description of the extraction model
        
    Returns:
        ExtractionModel: Created extraction model object
    """
    model = ExtractionModel(
        name=name,
        description=description,
        taxonomy_id=taxonomy_id,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        is_active=True
    )
    db.add(model)
    db.commit()
    db.refresh(model)
    return model

def get_extraction_model(db: Session, model_id: int) -> Optional[ExtractionModel]:
    """
    Get an extraction model by ID.
    
    Args:
        db (Session): Database session
        model_id (int): ID of the model to retrieve
        
    Returns:
        Optional[ExtractionModel]: Extraction model object if found, None otherwise
    """
    return db.query(ExtractionModel).filter(ExtractionModel.id == model_id).first()

def get_extraction_model_by_name(db: Session, name: str) -> Optional[ExtractionModel]:
    """
    Get an extraction model by name.
    
    Args:
        db (Session): Database session
        name (str): Name of the model to retrieve
        
    Returns:
        Optional[ExtractionModel]: Extraction model object if found, None otherwise
    """
    return db.query(ExtractionModel).filter(ExtractionModel.name == name).first()

def get_extraction_models(
    db: Session,
    taxonomy_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> List[ExtractionModel]:
    """
    Get a list of extraction models with optional filtering by taxonomy.
    
    Args:
        db (Session): Database session
        taxonomy_id (Optional[int]): Filter models by taxonomy ID
        skip (int): Number of records to skip
        limit (int): Maximum number of records to return
        
    Returns:
        List[ExtractionModel]: List of extraction model objects
    """
    query = db.query(ExtractionModel)
    if taxonomy_id:
        query = query.filter(ExtractionModel.taxonomy_id == taxonomy_id)
    return query.offset(skip).limit(limit).all()

def update_extraction_model(
    db: Session,
    model_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    is_active: Optional[bool] = None
) -> Optional[ExtractionModel]:
    """
    Update an extraction model's details.
    
    Args:
        db (Session): Database session
        model_id (int): ID of the model to update
        name (Optional[str]): New name for the model
        description (Optional[str]): New description for the model
        is_active (Optional[bool]): New active status for the model
        
    Returns:
        Optional[ExtractionModel]: Updated extraction model object if found, None otherwise
    """
    model = get_extraction_model(db, model_id)
    if model:
        if name is not None:
            model.name = name
        if description is not None:
            model.description = description
        if is_active is not None:
            model.is_active = is_active
        model.updated_at = datetime.now(UTC)
        db.commit()
        db.refresh(model)
    return model

def delete_extraction_model(db: Session, model_id: int) -> bool:
    """
    Delete an extraction model.
    
    Args:
        db (Session): Database session
        model_id (int): ID of the model to delete
        
    Returns:
        bool: True if model was deleted, False if not found
    """
    model = get_extraction_model(db, model_id)
    if model:
        db.delete(model)
        db.commit()
        return True
    return False
