from typing import List, Dict, Optional, Set

from utils.llm import OpenAI
from utils.doc_manipulation import get_docstrings_from_file, transform_file_lines


class Run:
    def __init__(
        self,
        read_file_path: str,
        overwrite: bool,
        context_path: str,
        write_file_path: Optional[str] = None,
    ):
        """
        Initialize the Run class.

        Args:
            read_file_path (str): Path to the file from which docstrings will be read.
            write_file_path (str, optional): Path to the file where transformed lines will be written. Defaults to None.
        """
        self.read_file_path = read_file_path
        self.overwrite = overwrite
        self.write_file_path = self._resolve_write_file_path(write_file_path)
        self.context_path = context_path
        self.llm = OpenAI()

    def _resolve_write_file_path(self, write_file_path: str) -> str:
        """
        If write_file_path is None, assign read path with an underscore
        prepended to the file name.

        Args:
            write_file_path: The path to the write file.

        Returns:
            The resolved write file path.

        """
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
        """
        Extract and convert docstrings using OpenAI.

        Args:
            to_change_key (str): Determine which types of docstrings should be replaced.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing original and predicted docstrings.
        """
        docstring_map = list(
            get_docstrings_from_file(self.read_file_path, to_change_key)
        )

        for i, d in enumerate(docstring_map):
            docstring_map[i].predicted_text = self.llm.predict(d.text)

        return docstring_map

    def _write_to_file(self, write_path: str):
        """
        Write transformed lines with new docstrings to the specified file.

        Args:
            write_path (str): Path to the file where transformed lines will be written.
        """
        docstring_map = self._extract_and_convert_docstring()
        file_lines = transform_file_lines(self.read_file_path, docstring_map)

        with open(write_path, "r+") as f:
            f.writelines(file_lines)

    def single_file_run(self):
        """
        Execute a single file operation based on the run type.

        Raises:
            AssertionError: If the run type is not supported.
            ValueError: If the run type does not match any of the predefined types.
        """
        self._write_to_file(self.read_file_path)
