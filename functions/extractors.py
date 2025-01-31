from abc import ABC, abstractmethod
from typing import Dict, Any
from models.DataModels import Document, ExtractionModel

class DocumentExtractor(ABC):
    """
    Abstract base class for document extractors.
    Extracts predictions from a document using a specific extraction model.
    """

    @abstractmethod
    def extract(self, document: Document, extraction_model: ExtractionModel, *args: Any, **kwargs: Any) -> Dict[str, str]:
        """
        Extract predictions from a document using the specified extraction model.

        Args:
            document (Document): The document to extract predictions from
            extraction_model (ExtractionModel): The model to use for extraction
            *args: Variable length argument list for additional extraction parameters
            **kwargs: Arbitrary keyword arguments for additional extraction parameters

        Returns:
            Dict[str, str]: Dictionary mapping field names to their extracted string values
        """
        pass



class PassingExtractor(DocumentExtractor):
    """
    A simple extractor that assigns 'PASS' to all fields in a document.
    Used primarily for testing validation flows.
    """
    def extract(self, document: Document, extraction_model: ExtractionModel, *args: Any, **kwargs: Any) -> Dict[str, str]:
        # Get all fields from the document's taxonomy
        fields = document.taxonomy.fields if document.taxonomy else []
        
        # Create dictionary with 'PASS' value for each field
        predictions = {
            field.name: "PASS" 
            for field in fields
        }
        
        return predictions


class HardcodeValuesExtractor(DocumentExtractor):
    """
    A simple extractor that assigns values in **kwargs to fields in a document.
    """
    def extract(self, document: Document, extraction_model: ExtractionModel, *args: Any, **kwargs: Any) -> Dict[str, str]:
        # Get all fields from the document's taxonomy
        fields = document.taxonomy.fields if document.taxonomy else []

        # Create dictionary with values from kwargs for each field
        predictions = {
            field.name: kwargs.get(field.name, "N/A")
            for field in fields
        }
        return predictions