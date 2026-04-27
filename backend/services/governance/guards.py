import re
import logging
from typing import Any, Dict, List, Union

logger = logging.getLogger(__name__)

class PIIScrubber:
    """
    Enterprise Governance Shield: Detects and masks PII in agent inputs/outputs.
    """
    
    # Simple regex patterns for common PII
    PATTERNS = {
        "secret_key": r"(?:sk|pk|key|secret)[-_]?[a-zA-Z0-9_-]{20,}",
        "email": r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b",
        "phone": r"\b(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
        "credit_card": r"\b(?:\d[ -]*?){13,16}\b",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b"
    }

    @classmethod
    def scrub(cls, data: Any) -> Any:
        if isinstance(data, str):
            return cls._scrub_string(data)
        elif isinstance(data, dict):
            return {k: cls.scrub(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [cls.scrub(item) for item in data]
        return data

    @classmethod
    def _scrub_string(cls, text: str) -> str:
        scrubbed = text
        for label, pattern in cls.PATTERNS.items():
            scrubbed = re.sub(pattern, f"<{label.upper()}_MASKED>", scrubbed, flags=re.IGNORECASE)
        return scrubbed

def scrub_pii(data: Any) -> Any:
    return PIIScrubber.scrub(data)
