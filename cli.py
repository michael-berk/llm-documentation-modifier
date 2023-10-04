import click
from llm_documentation_modifier.run import Run


@click.command()
@click.option(
    "--read-file-path",
    type=str,
    required=True,
    help="Path to the file with source docstrings.",
)
@click.option(
    "--overwrite",
    type=bool,
    required=False,
    default=False,
    help="If True, the read-file-path will be be overwritten.",
)
@click.option(
    "--context-path",
    type=str,
    required=False,
    default="./context/convert-to-google-style/v1/context.yaml",
    help="Path to the LLM prompot/context of interest.",
)
@click.option(
    "--write-file-path",
    type=str,
    required=False,
    help="Path to the file where transformed lines will be written.",
)
def cli(read_file_path, overwrite, context_path, write_file_path):
    """
    Execute a single file operation based on the given parameters and run type.
    """
    Run(read_file_path, overwrite, context_path, write_file_path).single_file_run()


if __name__ == "__main__":
    cli()
