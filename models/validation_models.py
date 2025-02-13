from typing import Optional, Dict

from pydantic import BaseModel


class FieldComparisonResult(BaseModel):
    field_name: str
    label_value: str
    prediction_value: str
    match: bool


class PerformanceMetric(BaseModel):
    name: str
    value: float
    sample_size: Optional[int] = 0


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


if __name__ == '__main__':
    p = PerformanceMetric(name='accuracy', value=100.0)
    p = PerformanceMetric(name='accuracy', value=100)