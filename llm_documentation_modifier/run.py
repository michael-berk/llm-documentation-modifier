import os
from typing import List, Dict, Optional, Set

from utils.llm import OpenAI
from utils.doc_manipulation import (
    get_docstrings_from_file,
    transform_file_lines,
    DocstringMap,
)
from utils.log import init_logger
from utils.general import get_file_paths_in_directory

_logger = init_logger()


class Run:
    def __init__(
        self,
        read_file_path: str,
        write_file_path: Optional[str],
        gateway_uri: str,
        gateway_route_name: str,
    ):
        self.read_file_path = read_file_path
        self.write_file_path = (
            read_file_path if write_file_path is None else write_file_path
        )
        self.llm = OpenAI(gateway_uri, gateway_route_name)

    def _extract_and_convert_docstring(
        self, _read_file_path: str, to_change_key: str = "function"
    ) -> List[DocstringMap]:
        """Iterate through file and return the modified DocstringMap list."""
        docstring_map = list(get_docstrings_from_file(_read_file_path, to_change_key))

        _logger.info(
            f"Converting {len(docstring_map)} docstrings from {_read_file_path}..."
        )

        for i, d in enumerate(docstring_map):
            _logger.info(f"Converting {i + 1} / {len(docstring_map)} docstrings.")

            docstring_map[i].predicted_text = self.llm.predict(d.text)
            _logger.info("Predicted text:\n\n" + docstring_map[i].predicted_text + "\n")
            _logger.info(f"Converted {i + 1} / {len(docstring_map)} docstrings.")
        return docstring_map

    def _single_file_run(self, _read_file_path: str, _write_file_path: str):
        """Perform docstring substitution for a single file.

        Args:
            _read_file_path: path of the file to read from
            _write_file_path: path of the file to write to

        """

        docstring_map = self._extract_and_convert_docstring(_read_file_path)
        file_lines = transform_file_lines(_read_file_path, docstring_map)

        _logger.info(f"Writing to {_write_file_path}")
        with open(_write_file_path, "w+") as f:
            f.writelines(file_lines)

    def run(self):
        if os.path.isdir(self.read_file_path):
            files_to_modify = get_file_paths_in_directory(self.read_file_path, ".py")
            _logger.info(
                "The read path is detected to be a directory. The write path parameter will be "
                "ignored and all files in the read directory will be transformed in place."
            )
            _logger.info(f"There are {len(files_to_modify)} files.")
            for file_path in files_to_modify:
                _logger.info(f"Modifying {file_path}")
                self._single_file_run(file_path, file_path)
        else:
            self._single_file_run(self.read_file_path, self.write_file_path)
