from typing import Optional
from dataclasses import dataclass


@dataclass
class DocstringMap:
    start_line_number: int = -1
    end_line_number: int = -1
    text: str = ""
    docstring_type: str = None
    predicted_text: Optional[str] = None

    def __post_init__(self):
        self.text = self.text.strip().strip('"""')
