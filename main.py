from llm_documentation_modifier.run import Run


if __name__ == "__main__":
    Run(
        read_file_path="/Users/michael.berk/dev/mlflow/doc-formatting/mlflow/mlflow/pmdarima.py"
    ).single_file_run(3)
