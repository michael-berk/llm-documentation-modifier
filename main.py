import click
from llm_documentation_modifier.run import Run


@click.command()
@click.option(
    "--run-type",
    type=int,
    required=True,
    help="Type of run to execute. Supported values are 1, 2, and 3.",
)
@click.option(
    "--read-file-path",
    type=str,
    required=True,
    help="Path to the file with source docstrings.",
)
@click.option(
    "--context-path",
    type=str,
    default="./context/convert-to-google-style/v1/context.yaml",
    help="Path to the LLM prompot/context of interest.",
)
@click.option(
    "--write-file-path",
    type=str,
    help="Path to the file where transformed lines will be written.",
)
@click.option(
    "--n-comparison-iterations",
    type=int,
    default=2,
    help="Number of times to compare predicted output.",
)
def cli(run_type, read_file_path, context, write_file_path, n_comparison_iterations):
    """
    Execute a single file operation based on the given parameters and run type.
    """
    runner = Run(read_file_path, context, write_file_path, n_comparison_iterations)
    runner.single_file_run(run_type)


if __name__ == "__main__":
    cli()
