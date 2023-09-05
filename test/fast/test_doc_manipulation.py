import pytest
from functools import lru_cache

import ast

from utils.doc_manipulation import (
    _get_docstrings_map,
    _get_list_chunks_not_in_index,
    _replace_lines,
)

_PMDARIMA_PATH = "./test/test_resources/pmdarima.py"


################# Helpers #############
@pytest.fixture
def pmdarima_docs():
    with open(_PMDARIMA_PATH, "r") as f:
        return f.read()


@lru_cache
def lru_get_docstrings_map(docs):
    return list(_get_docstrings_map(docs, to_change_key="all"))


def strings_are_equal(string_1: str, string_2: str) -> bool:
    lines_1 = string_1.strip().split("\n")
    lines_2 = string_2.strip().split("\n")
    return not any(a.strip() != b.strip() for a, b in zip(lines_1, lines_2))


################# Tests #############
def test_docstring_map_module(pmdarima_docs):
    doc = lru_get_docstrings_map(pmdarima_docs)[0]
    expected = """The ``mlflow.pmdarima`` module provides an API for logging and loading ``pmdarima`` models.
    This module exports univariate ``pmdarima`` models in the following formats:

    Pmdarima format
        Serialized instance of a ``pmdarima`` model using pickle.
    :py:mod:`mlflow.pyfunc`
        Produced for use by generic pyfunc-based deployment tools and for batch auditing
        of historical forecasts.

    .. code-block:: python
        :caption: Example

        import pandas as pd
        import mlflow
        import mlflow.pyfunc
        import pmdarima
        from pmdarima import auto_arima


        # Define a custom model class
        class PmdarimaWrapper(mlflow.pyfunc.PythonModel):
            def load_context(self, context):
                self.model = context.artifacts["model"]

            def predict(self, context, model_input):
                return self.model.predict(n_periods=model_input.shape[0])


        # Specify locations of source data and the model artifact
        SOURCE_DATA = "https://raw.githubusercontent.com/facebook/prophet/master/examples/example_retail_sales.csv"
        ARTIFACT_PATH = "model"

        # Read data and recode columns
        sales_data = pd.read_csv(SOURCE_DATA)
        sales_data.rename(columns={"y": "sales", "ds": "date"}, inplace=True)

        # Split the data into train/test
        train_size = int(0.8 * len(sales_data))
        train, _ = sales_data[:train_size], sales_data[train_size:]

        # Create the model
        model = pmdarima.auto_arima(train["sales"], seasonal=True, m=12)

        # Log the model
        with mlflow.start_run():
            wrapper = PmdarimaWrapper()
            mlflow.pyfunc.log_model(
                artifact_path="model",
                python_model=wrapper,
                artifacts={"model": mlflow.pyfunc.model_to_dict(model)},
            )


    .. _Pmdarima:
        http://alkaline-ml.com/pmdarima/
    """

    assert doc.start_line_number == 1
    assert doc.end_line_number == 57
    assert strings_are_equal(doc.text, expected)
    assert doc.docstring_type == ast.Module


def test_docstring_map_function_full(pmdarima_docs):
    doc = lru_get_docstrings_map(pmdarima_docs)[5]

    expected = """Load a ``pmdarima`` ``ARIMA`` model or ``Pipeline`` object from a local file or a run.

    :param model_uri: The location, in URI format, of the MLflow model. For example:

                      - ``/Users/me/path/to/local/model``
                      - ``relative/path/to/local/model``
                      - ``s3://my_bucket/path/to/model``
                      - ``runs:/<mlflow_run_id>/run-relative/path/to/model``
                      - ``mlflow-artifacts:/path/to/model``

                      For more information about supported URI schemes, see
                      `Referencing Artifacts <https://www.mlflow.org/docs/latest/tracking.html#
                      artifact-locations>`_.
    :param dst_path: The local filesystem path to which to download the model artifact.
                     This directory must already exist. If unspecified, a local output
                     path will be created.

    :return: A ``pmdarima`` model instance

    .. code-block:: python
        :caption: Example

        import pandas as pd
        import mlflow
        from mlflow.models import infer_signature
        import pmdarima
        from pmdarima.metrics import smape

        # Specify locations of source data and the model artifact
        SOURCE_DATA = "https://raw.githubusercontent.com/facebook/prophet/master/examples/example_retail_sales.csv"
        ARTIFACT_PATH = "model"

        # Read data and recode columns
        sales_data = pd.read_csv(SOURCE_DATA)
        sales_data.rename(columns={"y": "sales", "ds": "date"}, inplace=True)

        # Split the data into train/test
        train_size = int(0.8 * len(sales_data))
        train, test = sales_data[:train_size], sales_data[train_size:]

        with mlflow.start_run():
            # Create the model
            model = pmdarima.auto_arima(train["sales"], seasonal=True, m=12)

            # Calculate metrics
            prediction = model.predict(n_periods=len(test))
            metrics = {"smape": smape(test["sales"], prediction)}

            # Infer signature
            input_sample = pd.DataFrame(train["sales"])
            output_sample = pd.DataFrame(model.predict(n_periods=5))
            signature = infer_signature(input_sample, output_sample)

            # Log model
            input_example = input_sample.head()
            mlflow.pmdarima.log_model(
                model, ARTIFACT_PATH, signature=signature, input_example=input_example
            )

            # Get the model URI for loading
            model_uri = mlflow.get_artifact_uri(ARTIFACT_PATH)

        # Load the model
        loaded_model = mlflow.pmdarima.load_model(model_uri)

        # Forecast for the next 60 days
        forecast = loaded_model.predict(n_periods=60)

        print(f"forecast: {forecast}")

    .. code-block:: text
        :caption: Output

        forecast:
        234    382452.397246
        235    380639.458720
        236    359805.611219
        ...


    """

    assert doc.start_line_number == 410
    assert doc.end_line_number == 490
    assert strings_are_equal(doc.text, expected)
    assert doc.docstring_type == ast.FunctionDef


def test_docstring_map_function_params_and_return_no_description(pmdarima_docs):
    doc = lru_get_docstrings_map(pmdarima_docs)[-1]

    expected = """:param dataframe: Model input data.
    :param params: Additional parameters to pass to the model for inference.

                    .. Note:: Experimental: This parameter may change or be removed in a future
                                            release without warning.

    :return: Model predictions.
    """

    assert doc.start_line_number == 531
    assert doc.end_line_number == 539
    assert strings_are_equal(doc.text, expected)
    assert doc.docstring_type == ast.FunctionDef


def test_docstring_map_function_no_params_or_description(pmdarima_docs):
    doc = lru_get_docstrings_map(pmdarima_docs)[2]

    expected = """:return: The default Conda environment for MLflow Models produced by calls to
    :func:`save_model()` and :func:`log_model()`
    """

    assert doc.start_line_number == 119
    assert doc.end_line_number == 122
    assert strings_are_equal(doc.text, expected)
    assert doc.docstring_type == ast.FunctionDef


def test_get_list_chunks_not_in_index():
    array = list(range(20))
    indexes = [(2, 5), (7, 8), (15, 17)]

    observed = list(_get_list_chunks_not_in_index(array, indexes))
    expected = [[0, 1], [5, 6], [8, 9, 10, 11, 12, 13, 14], [17, 18, 19]]

    assert observed == expected
