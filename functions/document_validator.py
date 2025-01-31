from abc import ABC, abstractmethod
from typing import Any
from models.DataModels import Document, ExtractionModel

class DocumentValidator(ABC):
    """
    Abstract base class for document validators.
    Validates all predictions for a document according to defined rules.
    """

    @abstractmethod
    def validate(self, document: Document, extraction_model: ExtractionModel, *args: Any, **kwargs: Any) -> bool:
        """
        Validate all predictions for a document according to defined rules.

        Args:
            document (Document): The document object to validate
            extraction_model (ExtractionModel): The extraction model used for predictions
            *args: Variable length argument list for additional validation parameters
            **kwargs: Arbitrary keyword arguments for additional validation parameters

        Returns:
            bool: True if validation passes for all predictions, False otherwise
        """
        pass



class RequiredFieldsValidator(DocumentValidator):
    """
    Validates that all required fields in a document's taxonomy have predictions.
    """
    def validate(self, document: Document, extraction_model: ExtractionModel, *args: Any, **kwargs: Any) -> bool:
        # Get all required fields from the taxonomy
        required_fields = [field for field in document.taxonomy.fields if field.is_required]
        
        # Get all predictions for this document and model
        predictions = [p for p in document.predictions if p.model_id == extraction_model.id]
        
        # Check that each required field has at least one prediction
        predicted_field_ids = {p.field_id for p in predictions}
        for field in required_fields:
            if field.id not in predicted_field_ids:
                return False
        
        return True


class FieldTypeValidator(DocumentValidator):
    """
    Validates that all predictions in a document match their field's data type rules.
    """
    def validate(self, document: Document, extraction_model: ExtractionModel, *args: Any, **kwargs: Any) -> bool:
        from functions.field_validators import (
            DecimalNumberValidator,
            DateFormatValidator,
            StringLengthValidator
        )

        # Get all predictions for this document and model
        predictions = [p for p in document.predictions if p.model_id == extraction_model.id]
        
        # Validate each prediction according to its field's data type
        for prediction in predictions:
            field = prediction.field
            
            # Select appropriate validator based on field data type
            if field.data_type == "number":
                validator = DecimalNumberValidator()
                if not validator.validate(prediction):
                    return False
                    
            elif field.data_type == "date":
                validator = DateFormatValidator()
                if not validator.validate(prediction):
                    return False
                    
            elif field.data_type == "string":
                validator = StringLengthValidator()
                # Example: Validate string length is between 1 and 1000 characters
                if not validator.validate(prediction, min_length=1, max_length=1000):
                    return False
        
        return True


class MissingFieldsValidator(DocumentValidator):
    """
    Validates that all fields defined in the taxonomy have at least one prediction.
    """
    def validate(self, document: Document, extraction_model: ExtractionModel, *args: Any, **kwargs: Any) -> bool:
        # Get all predictions for this document and model
        predictions = [p for p in document.predictions if p.model_id == extraction_model.id]
        
        # Get all fields from the taxonomy
        taxonomy_fields = document.taxonomy.fields if document.taxonomy else []
        
        # Get set of field IDs that have predictions
        predicted_field_ids = {p.field_id for p in predictions}
        
        # Get set of all field IDs from taxonomy
        taxonomy_field_ids = {field.id for field in taxonomy_fields}
        
        # Check if any fields are missing predictions
        missing_fields = taxonomy_field_ids - predicted_field_ids
        
        # Return True if no fields are missing, False otherwise
        return len(missing_fields) == 0
