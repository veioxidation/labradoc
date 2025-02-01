import os
from typing import Dict, List

import pandas as pd
from sqlalchemy.orm import Session

# Import our services
from database import get_db
from models.DataModels import Taxonomy
from services.documents import upload_document, assign_labels
from services.organization_service import create_organization, get_organization_by_name
from services.taxonomy_service import create_taxonomy


def create_demo_taxonomy(db: Session, organization_id: int):
    """Create a sample taxonomy for document classification"""
    fields = [
        {
            "name": "document_type",
            "data_type": "string",
            "description": "Type of document",
            "is_required": True
        },
        {
            "name": "issue_date",
            "data_type": "date",
            "description": "Date document was issued",
            "is_required": True
        },
        {
            "name": "reference_number",
            "data_type": "string",
            "description": "Document reference number",
            "is_required": False
        }
    ]
    # Check if the taxonomy already exists for the organization
    existing_taxonomy = db.query(Taxonomy).filter_by(name="Document Classification",
                                                     organization_id=organization_id).first()
    if not existing_taxonomy:
        # If it doesn't exist, create the taxonomy
        return create_taxonomy(
            db=db,
            name="Document Classification",
            organization_id=organization_id,
            fields=fields,
            description="Basic document classification taxonomy"
        )
    else:
        print("Taxonomy 'Document Classification' already exists for this organization.")
        return existing_taxonomy


def upload_documents(db: Session, folder_path: str, organization_id: int):
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
    existing_org = get_organization_by_name(db, "Demo Organization")
    if not existing_org:
        # Create a new organization
        org = create_organization(
            db=db,
            name="Demo Organization",
            description="Organization for testing document processing"
        )
    else:
        org = existing_org

    # Create taxonomy for document classification
    taxonomy = create_demo_taxonomy(db, org.id)

    # Upload documents from test folder
    test_folder = "test/samples"
    upload_documents(db, test_folder, org.id)


if __name__ == "__main__":
    # You would need to set up your database session here
    main()
