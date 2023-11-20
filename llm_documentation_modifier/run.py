from typing import List, Dict, Optional, Set

from utils.llm import OpenAI
from utils.doc_manipulation import get_docstrings_from_file, transform_file_lines
from utils.log import init_logger

_logger = init_logger()


class Run:
    def __init__(
        self,
        read_file_path: str,
        overwrite: bool,
        write_file_path: Optional[str],
        gateway_uri: str,
        gateway_route_name: str,
    ):
        self.read_file_path = read_file_path
        self.write_file_path = self._resolve_write_file_path(write_file_path, overwrite)
        self.llm = OpenAI(gateway_uri, gateway_route_name)

    def _resolve_write_file_path(self, write_file_path: str, overwrite: bool) -> str:
        if overwrite:
            return self.read_file_path

        if write_file_path is not None:
            return write_file_path
        else:
            split_path = self.read_file_path.split("/")
            path, file_name = "/".join(split_path[:-1]), split_path[-1]
            new_file_name = "_" + file_name

            return path + "/" + new_file_name

    def _extract_and_convert_docstring(
        self, to_change_key: str = "function"
    ) -> List[Dict[str, str]]:
        docstring_map = list(
            get_docstrings_from_file(self.read_file_path, to_change_key)
        )
        _logger.info(f"Converting {len(docstring_map)} docstrings...")

        for i, d in enumerate(docstring_map):
            _logger.info(f"Converting {i + 1} / {len(docstring_map)} docstrings.")

            docstring_map[i].predicted_text = self.llm.predict(d.text)
            _logger.info("Predicted text:\n\n" + docstring_map[i].predicted_text + "\n")
            _logger.info(f"Converted {i + 1} / {len(docstring_map)} docstrings.")
        return docstring_map

    def _write_to_file(self, write_path: str):
        docstring_map = self._extract_and_convert_docstring()
        file_lines = transform_file_lines(self.read_file_path, docstring_map)

        _logger.info(f"Writing to {write_path}")
        with open(write_path, "w+") as f:
            f.writelines(file_lines)

    def single_file_run(self):
        self._write_to_file(self.write_file_path)
