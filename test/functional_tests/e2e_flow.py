import os
from typing import Dict, List

import pandas as pd
from sqlalchemy.orm import Session

# Import our services
from database import get_db
from functions.extractors import HardcodeValuesExtractor
from models.DataModels import Taxonomy, Document
from services.documents import upload_document, assign_labels, upload_documents_from_folder, get_document
from services.metrics import create_or_update_metric
from services.model import create_extraction_model, get_extraction_model_by_name
from services.organization_service import create_organization, get_organization_by_name
from services.taxonomy_service import create_taxonomy

from org_definition import fields, taxonomy_name, org_name, org_description, test_folder

from database import get_db
from test.functional_tests.document_definition import document_mapping
from test.functional_tests.extraction_flow import extract_and_assign_predictions
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

if ADD_DOCS_TO_ORG:
    # Uploading documents
    doc_definition = document_mapping

    # Upload documents from test folder
    upload_documents_from_folder(db, test_folder, org.id)


if LABELLING:
    from labels_definition import labels_to_assign
    # Example usage
    assign_labels_to_documents(organization_name=org_name,
                               taxonomy_name=taxonomy_name,
                               labels_to_assign=labels_to_assign)

if EXTRACTION:
    from test.functional_tests.org_definition import org_name, taxonomy_name, model_name

    extraction_model = create_extraction_model(organization_name=org_name,
                                               taxonomy_name=taxonomy_name,
                                               model_name=model_name)
    for doc in document_mapping:
        document = get_document(db, doc["document_id"])  # Obtain the document using the document ID
        if not document:
            print(f"Document with ID '{doc['document_id']}' not found.")
            continue

        # You would need to provide actual organization name, taxonomy name, document, and extraction model
        extract_and_assign_predictions(extraction_model, document, extractor, **doc['labels'])

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

        predictions = doc.predictions
        for pred in [p for p in predictions if p.model_id == model_id]:
            print(pred.field_name, pred.value)

        doc_results.append(compare_labels_and_predictions(db, doc.id, model_id))

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
