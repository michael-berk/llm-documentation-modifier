import ast
from itertools import zip_longest
from typing import List, Dict, Tuple, Iterator, Any
from dataclasses import dataclass

from utils.general import flatten, get_leading_whitespace
from utils.docstring_map import DocstringMap

_AST_TYPES_MAP = {
    "all": (ast.FunctionDef, ast.Module, ast.ClassDef),
    "function": (ast.FunctionDef,),
    "module": (ast.Module,),
    "class": (ast.ClassDef,),
}


######### Read ####################
def _get_node_type(node: ast.AST) -> str:
    if isinstance(node, ast.Module):
        return str(ast.Module)
    if isinstance(node, ast.FunctionDef):
        return str(ast.FunctionDef)
    if isinstance(node, ast.ClassDef):
        return str(ast.ClassDef)


def _get_docstrings_map(source_code: str, to_change_key: str) -> Iterator[DocstringMap]:
    """Yield DocstringMap objects for docstrings found in the source code.
    Note that rows ranges are 0-indexed and the end index is meant to be used as non-inclusive.
    """

    assert to_change_key in _AST_TYPES_MAP.keys()

    tree = ast.parse(source_code)

    for node in ast.walk(tree):
        if isinstance(node, _AST_TYPES_MAP[to_change_key]):
            if docstring := ast.get_docstring(node, clean=True):
                yield DocstringMap(
                    start_line_number=node.body[0].lineno,
                    end_line_number=node.body[0].end_lineno,
                    text=docstring,
                    docstring_type=_get_node_type(node),
                )


def get_docstrings_from_file(
    path: str, to_change_key: str = "all"
) -> Iterator[DocstringMap]:
    with open(path, "r") as file:
        return _get_docstrings_map(file.read(), to_change_key)


####################### Write ###################
def _get_list_chunks_not_in_index(
    list_to_split: List[Any],
    delimiter_tuples: List[Tuple[int, int]],
    inclusive: bool = False,
) -> Iterator[List[Any]]:
    """
    This function breaks `list_to_split` into chunks, where sections of the list that fall within the
    index ranges defined by `delimiter_tuples` are excluded. Essentially, it returns the portions of
    the list that are outside these delimiter ranges.
    """
    if inclusive:
        delimiter_tuples = [(a, b + 1) for a, b in delimiter_tuples]

    delimeter_indices_lookup = set(flatten([list(range(*d)) for d in delimiter_tuples]))
    current_chunk = []
    for i, line in enumerate(list_to_split):
        if i not in delimeter_indices_lookup:
            current_chunk.append(line)
        else:
            if current_chunk != []:
                yield current_chunk
                current_chunk = []

    yield current_chunk


def _replace_lines(
    file_lines: List[str], new_comments_line_mappings: Dict[DocstringMap, Any]
) -> Iterator[List[str]]:
    line_numbers = [
        (x.start_line_number, x.end_line_number - 1) for x in new_comments_line_mappings
    ]
    file_lines_to_keep = list(_get_list_chunks_not_in_index(file_lines, line_numbers))
    sorted_replacements = sorted(
        new_comments_line_mappings, key=lambda x: x.start_line_number
    )

    for raw_file, comment in zip_longest(
        file_lines_to_keep, sorted_replacements, fillvalue=None
    ):
        # Convert from string to list of lines
        if comment is None:
            predicted_lines = []
        else:
            predicted_lines = [l + "\n" for l in comment.predicted_text.split("\n")]

        # Handle replacement lists of differing length
        if raw_file:
            prepend_value = get_leading_whitespace(raw_file[-1])
        else:
            raw_file = []
            prepend_value = ""

        # Indent according to prior line in raw_file
        comment_indented = [prepend_value + x for x in predicted_lines]

        yield raw_file + comment_indented


def transform_file_lines(
    read_file_path: str, new_comments_line_mapping: Dict[DocstringMap, Any]
) -> List[str]:
    """
    Modify the lines of a file with new comments and return the new lines.
    """
    with open(read_file_path, "r") as f:
        old_file_lines = f.readlines()

    new_file_lines = list(_replace_lines(old_file_lines, new_comments_line_mapping))
    return flatten(new_file_lines)
