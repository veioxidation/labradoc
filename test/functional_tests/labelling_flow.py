from typing import Dict, List
from database import get_db
from services.documents import assign_labels
from services.organization_service import get_organization_by_name
from services.taxonomy_service import get_taxonomy_by_name

def assign_labels_to_documents(organization_name: str,
                               taxonomy_name: str,
                               labels_to_assign: List[Dict]):
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
    from org_definition import org_name, taxonomy_name
    from labels_definition import labels_to_assign
    # Example usage
    assign_labels_to_documents(organization_name=org_name,
                               taxonomy_name=taxonomy_name,
                               labels_to_assign=labels_to_assign)

