from typing import Dict, List

from requests import Session

from models.DataModels import FieldLabel
from models.validation_models import FieldComparisonResult, DocumentComparisonResult
from services.extractions import get_predictions_for_document_and_model


def compare_labels_and_predictions(db: Session,
                                   document_id: int,
                                   model_id: int) -> DocumentComparisonResult:
    """
    Compare document's labels and predictions from a specified model.

    Args:
        db (Session): Database session
        document_id (int): ID of the document to compare
        model_id (int): ID of the extraction model to use for predictions

    Returns:
        Dict[str, bool]: A dictionary with field names as keys and a boolean indicating match status as values
    """
    # Retrieve predictions for the document and model
    predictions = get_predictions_for_document_and_model(db, document_id, model_id)

    # Retrieve labels for the document
    field_labels = db.query(FieldLabel).filter(FieldLabel.document_id == document_id).all()

    # Create a mapping of field names to their values from predictions
    prediction_map = {pred.field_name: pred.value for pred in predictions}

    dcr = DocumentComparisonResult(document_id=document_id, model_id=model_id, field_results={})

    # Compare each field label with the corresponding prediction
    for label in field_labels:
        field_name = label.field_name
        label_value = label.value

        # Check if the field exists in predictions and compare values
        f = FieldComparisonResult(field_name=field_name,
                                  label_value=label_value,
                                  prediction_value=prediction_map[field_name] if field_name in prediction_map else "",
                                  match=(prediction_map[field_name] == label_value))
        dcr.field_results[field_name] = f
    return dcr


def get_accuracy_for_each_field(comparison_results: List[DocumentComparisonResult]) -> Dict[str, float]:
    """
    Calculate the accuracy rate for each field across multiple documents.

    Args:
        comparison_results (List[Dict[str, bool]]): A list of dictionaries with field names as keys and a boolean indicating match status as values

    Returns:
        Dict[str, float]: A dictionary with field names as keys and accuracy rates as values
    """
    # Get unique field names from all documents
    field_accuracies = {}
    field_names = comparison_results[0].document_fields
    for field in field_names:
        field_accuracies[field] = sum(
            [int(doc_result.field_results[field].match) for doc_result in comparison_results]) / len(
            comparison_results) * 100
    return field_accuracies


def get_percent_of_fully_correctly_extracted(comparison_results: List[DocumentComparisonResult]):
    """
    Calculate the percentage of documents that have all fields correctly extracted.

    Args:
        comparison_results (List[Dict[str, bool]]): A list of dictionaries with field names as keys and a boolean indicating match status as values

    Returns:
        float: Percentage of documents with all fields correctly extracted
    """
    correct_count = sum([1 for result in comparison_results if result.all_fields_correct()])
    return correct_count / len(comparison_results) * 100


def get_overall_accuracy(doc_results):
    return sum([result.accuracy_rate() for result in doc_results]) / len(doc_results) * 100
