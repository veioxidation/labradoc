from datetime import UTC, datetime
from sqlalchemy.orm import Session
from models.DataModels import Prediction, TaxonomyField, ExtractionModel, Document
from typing import Dict, List, Optional

def add_predictions(db: Session, model: ExtractionModel, document: Document, predictions: Dict[str, str]) -> bool:
    """
    Add predictions for a document using an extraction model.
    """
    # Check for existing predictions and delete them if present
    existing_predictions = db.query(Prediction).filter(
        Prediction.model_id == model.id,
        Prediction.document_id == document.id
    ).all()
    
    for prediction in existing_predictions:
        db.delete(prediction)
    
    # Create new predictions
    for field_name, value in predictions.items():
        field_id = db.query(TaxonomyField.id).filter(
            TaxonomyField.name == field_name,
            TaxonomyField.taxonomy_id == model.taxonomy.id
        ).first()[0]
        
        if field_id is None:
            raise ValueError(f"Field '{field_name}' not found for model ID '{model.id}'")

        new_prediction = Prediction(
            model_id=model.id,
            document_id=document.id,
            field_id=field_id,
            field_name=field_name,
            value=value,
            occurrence = 1
        )
        db.add(new_prediction)
    db.commit()

    return True

def get_predictions_for_document(db: Session, document_id: int) -> List[Prediction]:
    """
    Get all predictions for a given document.
    
    Args:
        db (Session): Database session
        document_id (int): ID of the document to retrieve predictions for
        
    Returns:
        List[Prediction]: List of prediction objects for the specified document
    """
    return db.query(Prediction).filter(Prediction.document_id == document_id).all()

def get_predictions_for_document_and_model(db: Session, document_id: int, model_id: int) -> List[Prediction]:
    """
    Get all predictions for a given document and extraction model combination.
    
    Args:
        db (Session): Database session
        document_id (int): ID of the document to retrieve predictions for
        model_id (int): ID of the extraction model to filter predictions
        
    Returns:
        List[Prediction]: List of prediction objects for the specified document and model
    """
    return db.query(Prediction).filter(
        Prediction.document_id == document_id,
        Prediction.model_id == model_id
    ).all()

def get_predictions_for_model(db: Session, model_id: int) -> List[Prediction]:
    """
    Get all predictions for a given extraction model.
    
    Args:
        db (Session): Database session
        model_id (int): ID of the extraction model to retrieve predictions for
        
    Returns:
        List[Prediction]: List of prediction objects for the specified extraction model
    """
    return db.query(Prediction).filter(Prediction.model_id == model_id).all()


def delete_predictions_for_document_and_model(db: Session, document_id: int, model_id: int) -> bool:
    """
    Delete all predictions for a given document and extraction model.
    
    Args:
        db (Session): Database session
        document_id (int): ID of the document to delete predictions for
        model_id (int): ID of the extraction model to filter predictions
        
    Returns:
        bool: True if predictions were deleted, False if none found
    """
    predictions = db.query(Prediction).filter(
        Prediction.document_id == document_id,
        Prediction.model_id == model_id
    )
    if predictions.count() > 0:
        predictions.delete(synchronize_session=False)
        db.commit()
        return True
    return False

