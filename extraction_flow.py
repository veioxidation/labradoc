from database import get_db
from models.DataModels import ExtractionModel, Document
from services.extractions import add_predictions
from services.taxonomy_service import get_taxonomy_by_name
from functions.extractors import DocumentExtractor, PassingExtractor  # Assuming you want to use the extractor interface

from services.documents import get_document

def extract_and_assign_predictions(organization_name: str,
                                   taxonomy_name: str,
                                   extractor: DocumentExtractor):
    db = get_db().__next__()

    # Retrieve taxonomy by name
    taxonomy = get_taxonomy_by_name(db, taxonomy_name)
    if not taxonomy:
        print(f"Taxonomy '{taxonomy_name}' not found.")
        return

    new_extraction_model = ExtractionModel(
        name="New Extraction Model",
        description="This is a newly created extraction model for testing purposes.",
        taxonomy_id=taxonomy.id,
        is_active=True
    )
    db.add(new_extraction_model)
    db.commit()
    print(f"New extraction model '{new_extraction_model.name}' created with ID: {new_extraction_model.id}")

    document_mapping = [
        {"file_name": "sample1.txt", "document_id": 1},
        {"file_name": "sample2.txt", "document_id": 2},
    ]

    for doc in document_mapping:
        document = get_document(db, doc["document_id"])  # Obtain the document using the document ID
        if not document:
            print(f"Document with ID '{doc['document_id']}' not found.")
            continue

        predictions = extractor.extract(document,
                                        new_extraction_model)
        print("Predictions:", predictions)
        if predictions:
            success = add_predictions(db=db, model=new_extraction_model, document=document, predictions=predictions)
            if success:
                print(f"Predictions assigned to document '{document.name}' using model '{new_extraction_model.name}'.")


if __name__ == "__main__":
    # You would need to provide actual organization name, taxonomy name, document, and extraction model
    extractor = PassingExtractor()
    extract_and_assign_predictions("Demo Organization", "Document Classification", extractor) 
