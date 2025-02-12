from dotenv import load_dotenv

from services.extractions import add_predictions

load_dotenv()

# Import our services
from functions.extractors import HardcodeValuesExtractor, DocumentExtractor
from models.DataModels import Document, ExtractionModel
from services.documents import upload_documents_from_folder, get_document, get_documents
from services.metrics import create_or_update_metric
from services.model import create_extraction_model, get_extraction_model_by_name
from services.organization_service import create_organization, get_organization_by_name
from services.taxonomy_service import get_taxonomy_by_name

from org_definition import taxonomy_name, org_name, org_description, test_folder, model_description

from database import get_db
from test.functional_tests.document_definition import document_mapping
from test.functional_tests.labelling_flow import assign_labels_to_documents
from test.functional_tests.organization_definition_flow import create_demo_taxonomy
from test.functional_tests.validation_flow import compare_labels_and_predictions, \
    get_percent_of_fully_correctly_extracted, get_accuracy_for_each_field

extractor = HardcodeValuesExtractor


db = get_db().__next__()
ORG_CREATION = False
ADD_DOCS_TO_ORG = False
LABELLING = True
EXTRACTION = True
MODEL_EVALUATION = True


# Organization_creation
if ORG_CREATION:
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
else:
    org = get_organization_by_name(db, org_name)

if ADD_DOCS_TO_ORG:
    # Uploading documents
    doc_definition = document_mapping

    # Upload documents from test folder
    upload_documents_from_folder(db, test_folder, org.id)

if LABELLING:
    from labels_definition import labels_to_assign, extractions_to_assign

    # Example usage
    assign_labels_to_documents(organization_name=org_name,
                               taxonomy_name=taxonomy_name,
                               labels_to_assign=labels_to_assign)

def extract_and_assign_predictions(extraction_model: ExtractionModel,
                                   document: Document,
                                   extractor: DocumentExtractor,
                                   **kwargs):

    predictions = extractor.extract(document, extraction_model, **kwargs)
    print("Predictions:", predictions)
    if predictions:
        success = add_predictions(db=db, model=extraction_model, document=document, predictions=predictions)
        if success:
            print(f"Predictions assigned to document '{document.name}' using model '{extraction_model.name}'.")

if EXTRACTION:
    from test.functional_tests.org_definition import org_name, taxonomy_name, model_name

    # Getting all documents from the organization
    docs = get_documents(db, organization_id=org.id)
    taxonomy = get_taxonomy_by_name(db, taxonomy_name)
    extraction_model = create_extraction_model(db=db,
                                               taxonomy_id=taxonomy.id,
                                               model_name=model_name,
                                               model_description=model_description)
    ext = extractor()
    for doc, extractions in zip(docs, extractions_to_assign):

        # You would need to provide actual organization name, taxonomy name, document, and extraction model
        extract_and_assign_predictions(extraction_model,
                                       doc,
                                       ext,
                                       **extractions['labels'])

if MODEL_EVALUATION:
    model = get_extraction_model_by_name(db, model_name)
    model_id = model.id

    # Aggregate predictions for each document.
    doc_results = []
    for doc in document_mapping:
        document: Document = get_document(db, doc['document_id'])

        if not document:
            print(f"Document with ID '{doc['document_id']}' not found.")
            continue

        predictions = document.predictions
        for pred in [p for p in predictions if p.model_id == model_id]:
            print(pred.field_name, pred.value)

        doc_results.append(compare_labels_and_predictions(db, document.id, model_id))

    field_accuracy = get_accuracy_for_each_field(doc_results)
    overall_accuracy = sum([result.accuracy_rate() for result in doc_results]) / len(doc_results) * 100
    perc_of_full_correct = get_percent_of_fully_correctly_extracted(doc_results)

    # Add to Metrics database - overall_accuracy, field_accuracy, perc_of_full_correct
    metrics = [
        {"name": "overall_accuracy", "value": overall_accuracy},
        {"name": "perc_of_full_correct", "value": perc_of_full_correct}
    ] + [{"name": f"{field}_accuracy", "value": value} for field, value in field_accuracy.items()]

    for metric in metrics:
        create_or_update_metric(db, metric["name"], metric["value"], len(doc_results), model_id)

    print(doc_results)
    print(f"Overall accuracy: {overall_accuracy}")
    print(f"Accuracy for each field: {field_accuracy}")
