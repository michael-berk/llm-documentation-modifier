import json
import os
import logging
from dataclasses import dataclass, field, asdict
from typing import List

from utils.docstring_map import DocstringMap

logger = logging.getLogger(__name__)

"""
{
    "n_total_records": int,
    "data": [
        {
            serialized_docstring_map_1,
            serialized_docstring_map_2,
            ...
        }
    ]
}
"""


@dataclass
class Checkpoint:
    file_path: str
    n_total_records: str = -1
    data: List[DocstringMap] = field(default_factory=list)

    def __post_init__(self):
        if os.path.isfile(self.file_path):
            self._deserialize()
        else:
            if self.n_total_records == -1:
                raise ValueError(
                    "When initializing an empty checkpoint, you must pass n_total_records."
                )
            self._serialize()

    def _serialize(self):
        with open(self.file_path, "w") as f:
            json.dump(
                {
                    "n_total_records": self.n_total_records,
                    "data": [asdict(d) for d in self.data],
                },
                f,
                indent=2,
            )

    def _deserialize(self):
        with open(self.file_path, "r") as f:
            raw_data = json.load(f)
            self.n_total_records = raw_data["n_total_records"]
            self.data = [DocstringMap(**d) for d in raw_data.get("data", [])]

    def is_complete(self) -> bool:
        self._deserialize()
        return self.n_total_records == len(self.data)

    def append(self, object: DocstringMap):
        self.data.append(object)
        self._serialize()

    def get_all(self):
        return self.data
