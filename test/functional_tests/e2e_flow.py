from database import get_db
# Import our services
from functions.extractors import HardcodeValuesExtractor
from functions.metrics import compare_labels_and_predictions, get_accuracy_for_each_field, \
    get_percent_of_fully_correctly_extracted, get_overall_accuracy
from models.validation_models import PerformanceMetric
from functions.post_processing import PostProcessor
from models.DataModels import Document, Taxonomy
from org_definition import taxonomy_name, org_name, org_description, test_folder, model_description, fields
from services.documents import upload_documents_from_folder, get_document, get_documents, \
    assign_labels
from services.extractions import extract_and_assign_predictions
from services.metrics import create_or_update_metric
from services.model import create_extraction_model, get_extraction_model_by_name
from services.organization_service import create_organization, get_organization_by_name
from services.taxonomy_service import get_taxonomy_by_name, create_taxonomy
from test.functional_tests.document_definition import document_mapping

from labels_definition import postprocessing_operations

db = get_db().__next__()
ORG_CREATION = False
ADD_DOCS_TO_ORG = False
LABELLING = False
EXTRACTION = True
MODEL_EVALUATION = True

# MODEL DEFINITION
extractor = HardcodeValuesExtractor()
post_processor = PostProcessor(postprocessing_operations)

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

    """Create a sample taxonomy for document classification"""
    # Check if the taxonomy already exists for the organization
    existing_taxonomy = db.query(Taxonomy).filter_by(name=taxonomy_name,
                                                     organization_id=org.id).first()
    if not existing_taxonomy:
        # If it doesn't exist, create the taxonomy
        taxonomy = create_taxonomy(db=db,
                                   name=taxonomy_name,
                                   organization_id=org.id,
                                   description=org_description,
                                   fields=fields)
    else:
        print("Taxonomy 'Document Classification' already exists for this organization.")
        taxonomy = existing_taxonomy

else:
    org = get_organization_by_name(db, name=org_name)
    taxonomy = get_taxonomy_by_name(db, name=taxonomy_name)

if ADD_DOCS_TO_ORG:
    # Uploading documents
    doc_definition = document_mapping

    # Upload documents from test folder
    upload_documents_from_folder(db, test_folder, org.id)

if LABELLING:
    from labels_definition import labels_to_assign, extractions_to_assign, postprocessing_operations

    for labels_set in labels_to_assign:
        # Example usage
        assign_labels(
            db=db,
            document_id=labels_set["document_id"],
            taxonomy_id=taxonomy.id,
            labels=labels_set["labels"]
        )

if EXTRACTION:
    from test.functional_tests.org_definition import org_name, taxonomy_name, model_name
    from labels_definition import extractions_to_assign    # hard-coded extractions - not needed for other extractions
    additional_args_list = extractions_to_assign
    # Getting all documents from the organization
    docs = get_documents(db, organization_id=org.id)
    extraction_model = get_extraction_model_by_name(db=db,
                                                    name=model_name)
    if not extraction_model:
        extraction_model = create_extraction_model(db=db,
                                                   taxonomy_id=taxonomy.id,
                                                   model_name=model_name,
                                                   model_description=model_description)

    # Running extraction for each document
    for doc, additional_args in zip(docs, additional_args_list):
        # You would need to provide actual organization name, taxonomy name, document, and extraction model
        extract_and_assign_predictions(db=db,
                                       extraction_model=extraction_model,
                                       post_processor=post_processor,
                                       document=doc,
                                       extractor=extractor,
                                       **additional_args['labels'])

    if MODEL_EVALUATION:
        model_id = extraction_model.id

        # Aggregate predictions for each document.
        doc_results = [compare_labels_and_predictions(db, doc['document_id'], model_id) for doc in document_mapping]

        # Minimal fields:
        field_accuracy = get_accuracy_for_each_field(doc_results)
        overall_accuracy = get_overall_accuracy(doc_results)
        perc_of_full_correct = get_percent_of_fully_correctly_extracted(doc_results)

        # Add to Metrics database - overall_accuracy, field_accuracy, perc_of_full_correct
        metrics = [
            PerformanceMetric(name='overall_accuracy', value=overall_accuracy, sample_size=len(doc_results)),
            PerformanceMetric(name='perc_of_full_correct', value=perc_of_full_correct, sample_size=len(doc_results)),
        ] + [PerformanceMetric(name=f"{field}_accuracy",
                               value=value) for field, value in field_accuracy.items()]

        for metric in metrics:
            create_or_update_metric(db, metric.name, metric.value, len(doc_results), model_id)

        # print(doc_results)
        print(f"{'='*20} METRICS {'='*20}")
        print(f"Overall accuracy: {overall_accuracy:.2f} %" )
        print(f"Percentage of fully correct documents: {perc_of_full_correct:.2f} %")
        print(f"Accuracy for each field: {field_accuracy} %")
        print(f"{'='*20} METRICS {'='*20}")
