import logging
from typing import List, Dict, Optional, Set

from utils.log import init_logger
from utils.llm import OpenAI
from utils.docstring_map import DocstringMap
from utils.doc_manipulation import get_docstrings_from_file, transform_file_lines
from utils.checkpoint import Checkpoint

logger = init_logger()
CHECKPOINT_PATH = "./checkpoint/checkpoint.json"
DELETE_CHECKPOINT = False


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
        self.checkpoint = Checkpoint.load(CHECKPOINT_PATH)

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

    def _write_to_file(self, write_path: str, docstring_map: List[DocstringMap]):
        file_lines = transform_file_lines(self.read_file_path, docstring_map)

        logging.info(f"Writing to {write_path}")
        with open(write_path, "w+") as f:
            f.writelines(file_lines)

    def single_file_run(self, to_change_key: str = "function"):
        docstring_map = list(
            get_docstrings_from_file(self.read_file_path, to_change_key)
        )
        docstrings_to_convert = docstring_map[self.checkpoint.get_last_written_index :]

        for d in docstrings_to_convert:
            d.predicted_text = self.llm.predict(d.text)
            self.checkpoint.add_pair(d)

        written_docstring_objects = self.checkpoint.get_data_values()
        self._write_to_file(self.write_file_path, written_docstring_objects)

        if DELETE_CHECKPOINT:
            logger.info(f"Deleting checkpoint file at path: {self.checkpoint.path}")
            self.checkpoint.delete()
