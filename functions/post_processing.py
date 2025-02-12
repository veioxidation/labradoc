from typing import Optional, Dict, List, Callable
from datetime import datetime

from functools import reduce

# Combine the functions into one
def compose(*functions):
    return reduce(lambda f, g: lambda x: g(f(x)), functions)


class PostProcessor:
    def __init__(self, operations_datapoint: Dict[str, List[Callable[[str], str]]]):
        self.operations_datapoint = operations_datapoint
    def process(self, predictions: Dict[str, str]) -> Dict[str, str]:
        """
        Converting predictions dictionary according to specified rules
        :param predictions:
        :return:
        """
        for pred_key in [p for p in predictions if p in self.operations_datapoint]:
            operations = self.operations_datapoint[pred_key]
            predictions[pred_key] = compose(*operations)(predictions[pred_key])

        return predictions

def normalize_whitespace(text: str) -> str:
    """
    Normalizes whitespace in a string by removing extra spaces, newlines and tabs.
    
    Args:
        text (str): Input text to normalize
        
    Returns:
        str: Text with normalized whitespace
    """
    # Replace multiple whitespace chars with single space
    normalized = ' '.join(text.split())
    return normalized.strip()


def remove_special_characters(text: str, keep_chars: Optional[str] = None) -> str:
    """
    Removes special characters from text while optionally keeping specified ones.
    
    Args:
        text (str): Input text to clean
        keep_chars (Optional[str]): String of special characters to preserve
        
    Returns:
        str: Text with special characters removed
    """
    import re
    
    if keep_chars:
        # Escape special regex chars in keep_chars
        keep_chars = re.escape(keep_chars)
        pattern = rf'[^a-zA-Z0-9{keep_chars}\s]'
    else:
        pattern = r'[^a-zA-Z0-9\s]'
        
    return re.sub(pattern, '', text)


def standardize_date_format(text: str, input_formats: list[str] = None) -> Optional[str]:
    """
    Attempts to parse a date string and convert it to standard ISO format (YYYY-MM-DD).
    
    Args:
        text (str): Input date string
        input_formats (list[str]): List of expected input date formats
        
    Returns:
        Optional[str]: Standardized date string in YYYY-MM-DD format, or None if parsing fails
    """

    if input_formats is None:
        input_formats = [
            '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d',
            '%m-%d-%Y', '%d-%m-%Y', '%Y-%m-%d',
            '%b %d, %Y', '%B %d, %Y'
        ]
    
    for fmt in input_formats:
        try:
            parsed_date = datetime.strptime(text.strip(), fmt)
            return parsed_date.strftime('%Y-%m-%d')
        except ValueError:
            continue
            
    return None


if __name__ == '__main__':
    preds = {
        "prediction1": "value1   ",
        "prediction2": "value2   ",
        "prediction3": "value3"
    }
    proc_functions = {'prediction1': [normalize_whitespace]}

    # Assuming a PostProcessor class exists that utilizes the FieldValidator
    post_processor = PostProcessor(proc_functions)
    results = post_processor.process(predictions=preds)
    print(results)
