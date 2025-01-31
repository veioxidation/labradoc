from sqlalchemy.orm import Session
from models.DataModels import Organization
from datetime import datetime, UTC
from typing import List, Optional

def create_organization(db: Session, name: str, description: Optional[str] = None) -> Organization:
    """
    Create a new organization.
    
    Args:
        db (Session): Database session
        name (str): Name of the organization
        description (Optional[str]): Description of the organization
        
    Returns:
        Organization: Created organization object
    """
    organization = Organization(
        name=name,
        description=description,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        is_active=True
    )
    db.add(organization)
    db.commit()
    db.refresh(organization)
    return organization

def get_organization(db: Session, organization_id: int) -> Optional[Organization]:
    """
    Get an organization by ID.
    
    Args:
        db (Session): Database session
        organization_id (int): ID of the organization to retrieve
        
    Returns:
        Optional[Organization]: Organization object if found, None otherwise
    """
    return db.query(Organization).filter(Organization.id == organization_id).first()

def get_organization_by_name(db: Session, name: str) -> Optional[Organization]:
    """
    Get an organization by name.
    
    Args:
        db (Session): Database session
        name (str): Name of the organization to retrieve
        
    Returns:
        Optional[Organization]: Organization object if found, None otherwise
    """
    return db.query(Organization).filter(Organization.name == name).first()

def get_organizations(db: Session, skip: int = 0, limit: int = 100) -> List[Organization]:
    """
    Get a list of organizations with pagination.
    
    Args:
        db (Session): Database session
        skip (int): Number of records to skip
        limit (int): Maximum number of records to return
        
    Returns:
        List[Organization]: List of organization objects
    """
    return db.query(Organization).offset(skip).limit(limit).all()

def update_organization(
    db: Session, 
    organization_id: int, 
    name: Optional[str] = None,
    description: Optional[str] = None,
    is_active: Optional[bool] = None
) -> Optional[Organization]:
    """
    Update an organization's details.
    
    Args:
        db (Session): Database session
        organization_id (int): ID of the organization to update
        name (Optional[str]): New name for the organization
        description (Optional[str]): New description for the organization
        is_active (Optional[bool]): New active status for the organization
        
    Returns:
        Optional[Organization]: Updated organization object if found, None otherwise
    """
    organization = get_organization(db, organization_id)
    if organization:
        if name is not None:
            organization.name = name
        if description is not None:
            organization.description = description
        if is_active is not None:
            organization.is_active = is_active
        organization.updated_at = datetime.now(UTC)
        db.commit()
        db.refresh(organization)
    return organization

def delete_organization(db: Session, organization_id: int) -> bool:
    """
    Delete an organization.
    
    Args:
        db (Session): Database session
        organization_id (int): ID of the organization to delete
        
    Returns:
        bool: True if organization was deleted, False if not found
    """
    organization = get_organization(db, organization_id)
    if organization:
        db.delete(organization)
        db.commit()
        return True
    return False

