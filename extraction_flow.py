from database import get_db
from models.DataModels import ExtractionModel, Document
from services.extractions import add_predictions
from services.taxonomy_service import get_taxonomy_by_name
from functions.extractors import DocumentExtractor, PassingExtractor, \
    HardcodeValuesExtractor  # Assuming you want to use the extractor interface

from services.documents import get_document

db = get_db().__next__()


def create_extraction_model(organization_name: str, taxonomy_name: str, model_name: str):
    # Retrieve taxonomy by name
    taxonomy = get_taxonomy_by_name(db, taxonomy_name)
    if not taxonomy:
        print(f"Taxonomy '{taxonomy_name}' not found.")
        return
    # Return a model object if one with the same name exists, otherwise create a new one
    existing_model = db.query(ExtractionModel).filter(ExtractionModel.name == model_name).first()
    if existing_model:
        print(f"Extraction model with name '{model_name}' already exists.")
        return existing_model

    extraction_model = ExtractionModel(
        name=model_name,
        description="This is a newly created extraction model for testing purposes.",
        taxonomy_id=taxonomy.id,
        is_active=True
    )
    db.add(extraction_model)
    db.commit()
    print(f"New extraction model '{extraction_model.name}' created with ID: {extraction_model.id}")
    return extraction_model

def extract_and_assign_predictions(extraction_model: ExtractionModel,
                                   document: Document,
                                   extractor: DocumentExtractor, **kwargs):

    predictions = extractor.extract(document, extraction_model, **kwargs)
    print("Predictions:", predictions)
    if predictions:
        success = add_predictions(db=db, model=extraction_model, document=document, predictions=predictions)
        if success:
            print(f"Predictions assigned to document '{document.name}' using model '{extraction_model.name}'.")


if __name__ == "__main__":
    # Example usage
    model_name = "Demo Extraction Model"
    extraction_model = create_extraction_model("Demo Organization",
                                               "Document Classification",
                                               model_name=model_name)

    document_mapping = [
        {"file_name": "sample1.txt", "document_id": 1, 'labels': {"document_type": "Invoice",
                                       "issue_date": "2023-01-01",
                                       "reference_number": "INV-001"}},
        {"file_name": "sample2.txt", "document_id": 2, 'labels': {"document_type":"Report",
                                       "issue_date": "2023-01-02",
                                       "reference_number": "RPT-002"}},
    ]

    for doc in document_mapping:
        document = get_document(db, doc["document_id"])  # Obtain the document using the document ID
        if not document:
            print(f"Document with ID '{doc['document_id']}' not found.")
            continue

        # You would need to provide actual organization name, taxonomy name, document, and extraction model
        extractor = HardcodeValuesExtractor()
        extract_and_assign_predictions(extraction_model, document, extractor, **doc['labels'])
