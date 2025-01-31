from abc import ABC, abstractmethod
from models.DataModels import Prediction
from typing import Any
import re

class FieldValidator(ABC):
    """
    Abstract base class for field validators.
    Validates prediction values according to field type and rules.
    """

    @abstractmethod
    def validate(self, prediction: Prediction, *args: Any, **kwargs: Any) -> bool:
        """
        Validate a prediction value according to the field's type and rules.

        Args:
            prediction (Prediction): The prediction object to validate
            *args: Variable length argument list for additional validation parameters
            **kwargs: Arbitrary keyword arguments for additional validation parameters

        Returns:
            bool: True if validation passes, False otherwise
        """
        pass



class DecimalNumberValidator(FieldValidator):
    """
    Validates that a prediction value is a valid decimal number.
    """
    def validate(self, prediction: Prediction, *args: Any, **kwargs: Any) -> bool:
        try:
            float(prediction.value)
            return True
        except ValueError:
            return False


class NumberRangeValidator(FieldValidator):
    """
    Validates that a numeric prediction value falls within a specified range.
    """
    def validate(self, prediction: Prediction, min_value: float = None, max_value: float = None, *args: Any, **kwargs: Any) -> bool:
        try:
            value = float(prediction.value)
            if min_value is not None and value < min_value:
                return False
            if max_value is not None and value > max_value:
                return False
            return True
        except ValueError:
            return False


class StringLengthValidator(FieldValidator):
    """
    Validates that a string prediction value is within specified length limits.
    """
    def validate(self, prediction: Prediction, max_length: int = None, min_length: int = None, *args: Any, **kwargs: Any) -> bool:
        value_length = len(str(prediction.value))
        if max_length is not None and value_length > max_length:
            return False
        if min_length is not None and value_length < min_length:
            return False
        return True


class DateFormatValidator(FieldValidator):
    """
    Validates that a prediction value matches a specified date format.
    """
    def validate(self, prediction: Prediction, date_format: str = "%Y-%m-%d", *args: Any, **kwargs: Any) -> bool:
        from datetime import datetime
        try:
            datetime.strptime(prediction.value, date_format)
            return True
        except ValueError:
            return False


class RegexValidator(FieldValidator):
    """
    Validates that a prediction value matches a specified regex pattern.
    """
    def validate(self, prediction: Prediction, pattern: str, *args: Any, **kwargs: Any) -> bool:
        try:
            return bool(re.match(pattern, prediction.value))
        except (TypeError, re.error):
            return False




class ISINValidator(FieldValidator):
    """
    Validates that a prediction value is a valid ISIN (International Securities Identification Number).
    ISIN format: 2 letters (country code) + 9 alphanumeric chars + 1 check digit
    """
    def validate(self, prediction: Prediction, *args: Any, **kwargs: Any) -> bool:
        # Basic format check
        if not isinstance(prediction.value, str):
            return False
            
        isin = prediction.value.strip().upper()
        if len(isin) != 12:
            return False
            
        # Check country code (first 2 chars are letters)
        if not isin[:2].isalpha():
            return False
            
        # Check middle 9 chars are alphanumeric
        if not isin[2:-1].isalnum():
            return False
            
        # Validate check digit
        try:
            # Convert letters to numbers (A=10, B=11, etc)
            values = []
            for char in isin[:-1]:
                if char.isalpha():
                    values.append(str(ord(char) - ord('A') + 10))
                else:
                    values.append(char)
                    
            # Double alternate digits from right to left
            num = ''.join(values)
            total = 0
            for i, digit in enumerate(reversed(num)):
                n = int(digit)
                if i % 2 == 0:
                    n *= 2
                    if n > 9:
                        n -= 9
                total += n
                
            check_digit = (10 - (total % 10)) % 10
            return str(check_digit) == isin[-1]
            
        except (ValueError, TypeError):
            return False


class CUSIPValidator(FieldValidator):
    """
    Validates that a prediction value is a valid CUSIP (Committee on Uniform Security Identification Procedures).
    CUSIP format: 9 characters - first 6 are alphanumeric issuer code, 2 alphanumeric issue number, 1 check digit
    """
    def validate(self, prediction: Prediction, *args: Any, **kwargs: Any) -> bool:
        if not isinstance(prediction.value, str):
            return False
            
        cusip = prediction.value.strip().upper()
        if len(cusip) != 9:
            return False
            
        # Check first 8 chars are alphanumeric
        if not cusip[:-1].isalnum():
            return False
            
        try:
            # Convert letters to numbers (A=10, B=11, etc)
            values = []
            for char in cusip[:-1]:
                if char.isalpha():
                    values.append(str(ord(char) - ord('A') + 10))
                else:
                    values.append(char)
                    
            # Calculate weighted sum
            total = 0
            for i, digit in enumerate(values):
                n = int(digit)
                if i % 2 == 1:
                    n *= 2
                total += sum(int(d) for d in str(n))
                
            check_digit = (10 - (total % 10)) % 10
            return str(check_digit) == cusip[-1]
            
        except (ValueError, TypeError):
            return False


class TradeDateValidator(FieldValidator):
    """
    Validates that a prediction value is a valid trade date (not weekend or major US holiday).
    """
    def validate(self, prediction: Prediction, *args: Any, **kwargs: Any) -> bool:
        from datetime import datetime
        
        try:
            # First validate basic date format
            date = datetime.strptime(prediction.value, "%Y-%m-%d")
            
            # Check if weekend
            if date.weekday() >= 5:  # 5=Saturday, 6=Sunday
                return False
                
            # Major US holidays (simplified list)
            holidays = [
                (1, 1),    # New Year's Day
                (7, 4),    # Independence Day
                (12, 25),  # Christmas
            ]
            
            if (date.month, date.day) in holidays:
                return False
                
            return True
            
        except ValueError:
            return False

