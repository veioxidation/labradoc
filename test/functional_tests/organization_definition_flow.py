import os
from typing import Dict, List

import pandas as pd
from sqlalchemy.orm import Session

# Import our services
from database import get_db
from models.DataModels import Taxonomy
from services.documents import upload_document, assign_labels, upload_documents_from_folder
from services.organization_service import create_organization, get_organization_by_name
from services.taxonomy_service import create_taxonomy

from org_definition import fields, taxonomy_name, org_name, org_description, test_folder


def create_demo_taxonomy(db: Session, organization_id: int):
    """Create a sample taxonomy for document classification"""
    # Check if the taxonomy already exists for the organization
    existing_taxonomy = db.query(Taxonomy).filter_by(name=taxonomy_name,
                                                     organization_id=organization_id).first()
    if not existing_taxonomy:
        # If it doesn't exist, create the taxonomy
        return create_taxonomy(
            db=db,
            name=taxonomy_name,
            organization_id=organization_id,
            fields=fields,
            description=org_description
        )
    else:
        print("Taxonomy 'Document Classification' already exists for this organization.")
        return existing_taxonomy




def apply_labels_from_excel(db: Session, excel_path: str, document_mapping: List[Dict], taxonomy_id: int):
    """Apply labels from Excel file to documents"""
    # Read Excel file containing labels
    df = pd.read_excel(excel_path)

    # Create a mapping of filenames to document IDs
    filename_to_doc_id = {doc["file_name"]: doc["document_id"] for doc in document_mapping}

    for _, row in df.iterrows():
        document_id = filename_to_doc_id.get(row['file_name'])
        if document_id:
            # Create labels dictionary from Excel columns
            labels = {
                "document_type": row['document_type'],
                "issue_date": row['issue_date'].strftime('%Y-%m-%d'),
                "reference_number": row['reference_number']
            }

            # Assign labels to document
            assign_labels(
                db=db,
                document_id=document_id,
                taxonomy_id=taxonomy_id,
                labels=labels
            )


def main():
    db = get_db().__next__()

    # Check if the organization already exists
    existing_org = get_organization_by_name(db, org_name)
    if not existing_org:
        # Create a new organization
        org = create_organization(
            db=db,
            name=org_name,
            description=org_description
        )
    else:
        org = existing_org

    # Create taxonomy for document classification
    create_demo_taxonomy(db, org.id)

    # Upload documents from test folder
    upload_documents_from_folder(db, test_folder, org.id)


if __name__ == "__main__":
    # You would need to set up your database session here
    main()
