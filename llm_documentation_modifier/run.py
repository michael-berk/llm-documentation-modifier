from typing import List, Dict, Tuple, Optional, Set

from utils.llm import OpenAI
from utils.doc_manipulation import get_docstrings_from_file, transform_file_lines

_SUPPORTED_RUNS = {1, 2, 3}


class Run:
    def __init__(
        self,
        read_file_path: str,
        write_file_path: Optional[str] = None,
        n_comparison_iterations: Optional[int] = 2,
    ):
        """
        Initialize the Run class.

        Args:
            read_file_path (str): Path to the file from which docstrings will be read.
            write_file_path (str, optional): Path to the file where transformed lines will be written. Defaults to None.
            n_comparison_iterations (int, optional): Number of times to compare for variance test. Defaults to 2.
        """
        self.read_file_path = read_file_path
        self.write_file_path = write_file_path
        self.n_comparison_operations = n_comparison_iterations
        self.llm = OpenAI()

    def _extract_and_convert_docstring(self) -> List[Dict[str, str]]:
        """
        Extract and convert docstrings using OpenAI.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing original and predicted docstrings.
        """
        docstring_map = list(get_docstrings_from_file(self.read_file_path))

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

    def _variance_test(self):
        """
        Run the variance test to determine how much the predicted docstrings vary over multiple runs.
        """
        output = {}  # type: Dict[str, Set[str]]
        for i in range(self.n_comparison_operations):
            print(f"Running iteration: {i}")
            docstring_map = self._extract_and_convert_docstring()
            for docstring in docstring_map:
                key = docstring.text
                value = "\n".join(docstring.predicted_text)

                current_value = output.get(key, set())
                current_value.add(value)

                output[key] = current_value

        percent_match = {
            k: 100 * len(v) / self.n_comparison_operations for k, v in output.items()
        }
        for k, v in percent_match.items():
            print("------------------\n" * 5)
            print(k)
            print(v)
            if v != 100:
                print('------------- {k} ------------\n'*4)
                for vv in output[k]:
                    print(vv)
                print('------------- {k} ------------\n'*4)

        print(f"Overall equality by index: {percent_match.values()}")

    def single_file_run(self, run_type: int):
        """
        Execute a single file operation based on the run type.

        Args:
            run_type (int): Type of run to execute. Supported values are in the _SUPPORTED_RUNS set.

        Raises:
            AssertionError: If the run type is not supported.
            ValueError: If the run type does not match any of the predefined types.
        """
        assert (
            run_type in _SUPPORTED_RUNS
        ), f"Run type {run_type} must be in {_SUPPORTED_RUNS}"

        if run_type == 1:  # Overwrite
            self._write_to_file(self.read_file_path)
        elif run_type == 2:  # Temp File
            self._write_to_file(self.write_file_path)
        elif run_type == 3:  # Repeat and compare
            self._variance_test()
        else:
            raise ValueError(f"Run type {run_type} is not supported.")
