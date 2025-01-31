from typing import Optional

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
        pattern = f'[^a-zA-Z0-9{keep_chars}\s]'
    else:
        pattern = '[^a-zA-Z0-9\s]'
        
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
    from datetime import datetime
    
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
