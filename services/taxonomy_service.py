
from sqlalchemy.orm import Session
from models.DataModels import FieldLabel, Taxonomy, TaxonomyField
from typing import List, Optional, Dict

from services.documents import get_document

def create_taxonomy(
    db: Session,
    name: str,
    organization_id: int,
    fields: List[Dict],
    description: Optional[str] = None,
    version: str = "1.0",
) -> Taxonomy:
    """
    Create a new taxonomy with fields.
    
    Args:
        db (Session): Database session
        name (str): Name of the taxonomy
        organization_id (int): ID of the organization this taxonomy belongs to
        fields (List[Dict]): List of field definitions, each containing:
            - name (str): Field name
            - data_type (str): Data type of the field
            - description (str, optional): Field description
            - is_required (bool, optional): Whether field is required
        description (Optional[str]): Description of the taxonomy
        version (str): Version of the taxonomy
        
    Returns:
        Taxonomy: Created taxonomy object with associated fields
    """
    # Create the taxonomy
    taxonomy = Taxonomy(
        name=name,
        description=description,
        version=version,
        organization_id=organization_id,
        is_active=True
    )
    db.add(taxonomy)
    db.flush()  # Flush to get the taxonomy ID
    
    # Create the fields
    for field_def in fields:
        field = TaxonomyField(
            name=field_def["name"],
            data_type=field_def["data_type"],
            description=field_def.get("description"),
            is_required=field_def.get("is_required", False),
            taxonomy_id=taxonomy.id
        )
        db.add(field)
    
    db.commit()
    db.refresh(taxonomy)
    return taxonomy

def get_taxonomy(db: Session, taxonomy_id: int) -> Optional[Taxonomy]:
    """
    Get a taxonomy by ID.
    
    Args:
        db (Session): Database session
        taxonomy_id (int): ID of the taxonomy to retrieve
        
    Returns:
        Optional[Taxonomy]: Taxonomy object if found, None otherwise
    """
    return db.query(Taxonomy).filter(Taxonomy.id == taxonomy_id).first()

def get_taxonomy_by_name(db: Session, name: str) -> Optional[Taxonomy]:
    """
    Get a taxonomy by name.
    
    Args:
        db (Session): Database session
        name (str): Name of the taxonomy to retrieve
        
    Returns:
        Optional[Taxonomy]: Taxonomy object if found, None otherwise
    """
    return db.query(Taxonomy).filter(Taxonomy.name == name).first()

def get_taxonomies(
    db: Session,
    organization_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Taxonomy]:
    """
    Get a list of taxonomies with optional filtering by organization.
    
    Args:
        db (Session): Database session
        organization_id (Optional[int]): Filter taxonomies by organization ID
        skip (int): Number of records to skip
        limit (int): Maximum number of records to return
        
    Returns:
        List[Taxonomy]: List of taxonomy objects
    """
    query = db.query(Taxonomy)
    if organization_id:
        query = query.filter(Taxonomy.organization_id == organization_id)
    return query.offset(skip).limit(limit).all()

def update_taxonomy(
    db: Session,
    taxonomy_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    version: Optional[str] = None,
    is_active: Optional[bool] = None,
    fields: Optional[List[Dict]] = None
) -> Optional[Taxonomy]:
    """
    Update a taxonomy's details and optionally its fields.
    
    Args:
        db (Session): Database session
        taxonomy_id (int): ID of the taxonomy to update
        name (Optional[str]): New name for the taxonomy
        description (Optional[str]): New description for the taxonomy
        version (Optional[str]): New version for the taxonomy
        is_active (Optional[bool]): New active status for the taxonomy
        fields (Optional[List[Dict]]): New field definitions. Each field dict should contain:
            - name (str): Field name
            - data_type (str): Data type of the field (e.g., "string", "number", "date")
            - description (Optional[str]): Field description
            - is_required (Optional[bool]): Whether field is required
        
    Returns:
        Optional[Taxonomy]: Updated taxonomy object if found, None otherwise
    """
    taxonomy = get_taxonomy(db, taxonomy_id)
    if taxonomy:
        if name is not None:
            taxonomy.name = name
        if description is not None:
            taxonomy.description = description
        if version is not None:
            taxonomy.version = version
        if is_active is not None:
            taxonomy.is_active = is_active
            
        if fields is not None:
            # Remove existing fields
            db.query(TaxonomyField).filter(TaxonomyField.taxonomy_id == taxonomy_id).delete()
            
            # Add new fields
            for field_def in fields:
                field = TaxonomyField(
                    name=field_def["name"],
                    data_type=field_def["data_type"],
                    description=field_def.get("description"),
                    is_required=field_def.get("is_required", False),
                    taxonomy_id=taxonomy_id
                )
                db.add(field)
        
        db.commit()
        db.refresh(taxonomy)
    return taxonomy

def delete_taxonomy(db: Session, taxonomy_id: int) -> bool:
    """
    Delete a taxonomy and its associated fields.
    
    Args:
        db (Session): Database session
        taxonomy_id (int): ID of the taxonomy to delete
        
    Returns:
        bool: True if taxonomy was deleted, False if not found
    """
    taxonomy = get_taxonomy(db, taxonomy_id)
    if taxonomy:
        db.delete(taxonomy)
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
                value=value
            )
            db.add(label)
    
    document.taxonomy_id = taxonomy_id
    document.is_labeled = True
    db.commit()
    return True
