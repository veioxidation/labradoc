from typing import Dict, List
from requests import Session

from database import get_db
from models.DataModels import Prediction, FieldLabel
from services.documents import get_document
from services.extractions import get_predictions_for_document_and_model

from pydantic import BaseModel

from services.metrics import create_or_update_metric
from services.model import get_extraction_model_by_name
from test.functional_tests.org_definition import model_name


class FieldComparisonResult(BaseModel):
    field_name: str
    label_value: str
    prediction_value: str
    match: bool


class DocumentComparisonResult(BaseModel):
    document_id: int
    model_id: int
    field_results: Dict[str, FieldComparisonResult]

    def __str__(self):
        return f"Document ID: {self.document_id}, Model ID: {self.model_id}, Field Results: {self.field_results}"

    def all_fields_correct(self):
        return all([field.match for field in self.field_results.values()])

    def incorrect_fields(self):
        return [field for field in self.field_results.values() if not field.match]

    def correct_fields(self):
        return [field for field in self.field_results.values() if field.match]

    def incorrect_fields_string(self):
        return "Incorrect fields: " + ", ".join([field.field_name for field in self.incorrect_fields()])

    def accuracy_rate(self):
        return len(self.correct_fields()) / len(self.field_results)

    @property
    def document_fields(self):
        return self.field_results.keys()


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


if __name__ == "__main__":
    # You would need to provide actual document ID and extraction model ID
    db = get_db().__next__()
    model = get_extraction_model_by_name(db, model_name)
    model_id = model.id


    document_ids = [1, 2]
    doc_results = []
    for document_id in document_ids:
        doc = get_document(db, document_id)

        predictions = doc.predictions

        for pred in [p for p in predictions if p.model_id == model_id]:
            print(pred.field_name, pred.value)

        doc_results.append(compare_labels_and_predictions(db, document_id, model_id))

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
