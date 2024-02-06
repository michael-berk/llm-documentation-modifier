import os
import yaml
from typing import List, Any, Union, Dict


def get_file_paths_in_directory(directory: str, suffix: str = ""):
    return sorted(
        [
            os.path.join(root, file)
            for root, _, files in os.walk(directory)
            for file in files
            if file.endswith(suffix)
        ]
    )


def read_yaml(file_path: str) -> Union[Dict, List[Any], None]:
    with open(file_path, "r") as f:
        return yaml.safe_load(f)


def flatten(list_to_flatten: List[List[Any]]) -> List[Any]:
    return [item for sublist in list_to_flatten for item in sublist]


def get_leading_whitespace(s: str) -> str:
    return s[: len(s) - len(s.lstrip())]


def clean_and_split_comment(comment: str) -> List[str]:
    return [x + "\n" for x in comment.split("\n") if x.strip() != '"""']


def lines_are_equal(list1: list, list2: list) -> bool:
    return len(list1) == len(list2) and all(
        a.strip() == b.strip() for a, b in zip(list1, list2)
    )
