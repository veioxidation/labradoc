from database import get_db
from services.documents import assign_labels
from services.organization_service import get_organization_by_name
from services.taxonomy_service import get_taxonomy_by_name

def assign_labels_to_documents(organization_name: str, taxonomy_name: str):
    db = get_db().__next__()

    # Retrieve organization by name
    organization = get_organization_by_name(db, organization_name)
    if not organization:
        print(f"Organization '{organization_name}' not found.")
        return

    # Retrieve taxonomy by name
    taxonomy = get_taxonomy_by_name(db, taxonomy_name)
    if not taxonomy:
        print(f"Taxonomy '{taxonomy_name}' not found.")
        return
    
    labels_to_assign = [
        {"document_id": 1, "labels": {"document_type": "Invoice",
                                      "issue_date": "2021-01-15",
                                      "reference_number": "INV-001"}},
        {"document_id": 2, "labels": {"document_type":"Receipt",
                                      "issue_date": "2021-02-20",
                                      "reference_number": "REC-002"}},
    ]

    # Example document mapping (this would typically come from your document processing logic)
    document_mapping = [
        {"file_name": "sample1.txt", "document_id": 1},
        {"file_name": "sample2.txt", "document_id": 2},
    ]

    # Assign labels to documents
    for label_info in labels_to_assign:
        assign_labels(
            db=db,
            document_id=label_info["document_id"],
            taxonomy_id=taxonomy.id,
            labels=label_info["labels"]
        )

    print(f"Labels assigned to documents for organization '{organization_name}' and taxonomy '{taxonomy_name}'.")

if __name__ == "__main__":
    # Example usage
    assign_labels_to_documents("Demo Organization", "Document Classification")

