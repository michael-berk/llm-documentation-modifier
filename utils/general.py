import yaml
from typing import List, Any, Union


def read_yaml(file_path: str) -> Union[dict, List[Any], None]:
    """
    Reads and parses a YAML file.

    Args:
        file_path (str): The path to the YAML file.

    Returns:
        Union[dict, List[Any], None]: The parsed contents of the YAML file.
    """
    with open(file_path, "r") as f:
        return yaml.safe_load(f)


def flatten(list_to_flatten: List[List[Any]]) -> List[Any]:
    """
    Flattens a list of lists into a single list.

    Args:
        list_to_flatten (List[List[Any]]): The nested list to flatten.

    Returns:
        List[Any]: The flattened list.
    """
    return [item for sublist in list_to_flatten for item in sublist]


def get_leading_whitespace(s: str) -> str:
    """
    Retrieves the leading whitespace characters from a string.

    Args:
        s (str): The input string.

    Returns:
        str: The leading whitespace characters.
    """
    return s[: len(s) - len(s.lstrip())]


def clean_and_split_comment(comment: str) -> List[str]:
    """
    Splits a comment string by newline characters and filters out lines with '\"\"\"'.

    Args:
        comment (str): The comment string to split and clean.

    Returns:
        List[str]: A list of cleaned comment lines.
    """
    return [x + "\n" for x in comment.split("\n") if x.strip() != '"""']


def lines_are_equal(list1: list, list2: list) -> bool:
    """Check if two lists of strings are equal after stripping each string.

    Args:
        list1 (list): The first list of strings.
        list2 (list): The second list of strings.

    Returns:
        bool: True if the lists are equal after stripping, else False.
    """
    return len(list1) == len(list2) and all(
        a.strip() == b.strip() for a, b in zip(list1, list2)
    )
