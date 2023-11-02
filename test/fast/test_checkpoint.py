import ast
import pytest
import json
import tempfile
from unittest.mock import mock_open, patch

from utils.checkpoint import Checkpoint
from utils.docstring_map import DocstringMap

N_TOTAL_RECORDS = 3


@pytest.fixture
def temp_file():
    with tempfile.NamedTemporaryFile(mode="w+", delete=True) as f:
        json.dump({"n_total_records": N_TOTAL_RECORDS, "data": []}, f)
        f.flush()
        yield f.name


@pytest.fixture
def docstring_map():
    return DocstringMap(
        start_line_number=1,
        end_line_number=15,
        text="""This is my docstring.""",
        docstring_type=str(ast.FunctionDef),
        predicted_text=""""This is my new docstring.""",
    )


def test_raises_no_n_total_records():
    with pytest.raises(ValueError):
        Checkpoint("x.json")


def test_new_file_created_if_not_found():
    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        Checkpoint("x.json", 1)

    mock_file.assert_called_once_with("x.json", "w")


def test_get_all_data(docstring_map, temp_file):
    checkpoint = Checkpoint(temp_file)
    assert checkpoint.get_all() == []

    checkpoint.append(docstring_map)
    checkpoint.append(docstring_map)
    checkpoint.append(docstring_map)
    assert len(checkpoint.get_all()) == N_TOTAL_RECORDS
    assert all(isinstance(x, DocstringMap) for x in checkpoint.get_all())
    assert checkpoint.get_all()[0].end_line_number == 15


def test_is_complete(docstring_map, temp_file):
    checkpoint = Checkpoint(temp_file)
    assert not checkpoint.is_complete()

    checkpoint.append(docstring_map)
    checkpoint.append(docstring_map)
    checkpoint.append(docstring_map)
    assert checkpoint.is_complete()


def test_e2e(docstring_map, temp_file):
    checkpoint = Checkpoint(temp_file)
    while not checkpoint.is_complete():
        checkpoint.append(docstring_map)

    assert len(checkpoint.get_all()) == N_TOTAL_RECORDS
