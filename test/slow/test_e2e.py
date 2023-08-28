from llm_documentation_modifier.run import Run
from utils.doc_manipulation import transform_file_lines

from itertools import zip_longest

_PMDARIMA_PATH = "test/test_resources/pmdarima.py"
_PMDARIMA_CONVERTED_PATH = "test/test_resources/pmdarima_converted.py"
_CONTEXT_PATH = "context/convert-to-google-style-params-only/context.yaml"


def test_e2e_no_write():
    run = Run(_PMDARIMA_PATH, _CONTEXT_PATH)
    docstring_map = run._extract_and_convert_docstring(to_change_key="function")
    observed = transform_file_lines(_PMDARIMA_PATH, docstring_map)

    with open(_PMDARIMA_CONVERTED_PATH, "r") as f:
        expected = f.readlines()

    with open("/Users/michael.berk/Desktop/_pmdarima.py", "w+") as f:
        f.write("".join(observed))
    #for observed_line, expected_line in zip_longest(observed, expected, fillvalue=[""]):
    #    assert observed_line == expected_line

    observed = ''.join(observed).replace('\\n','').replace('\n','')
    expected = ''.join(expected).replace('\\n','').replace('\n','')
    assert observed == expected
