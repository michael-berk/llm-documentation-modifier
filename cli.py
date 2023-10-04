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
    "--write-file-path",
    type=str,
    required=False,
    default=None,
    help="Path to the file where transformed lines will be written.",
)
@click.option(
    "--gateway-uri",
    type=str,
    required=False,
    default="http://localhost:5000",
    help="URI for the mlflow gateway URI serving the LLM",
)
@click.option(
    "--gateway-route-name",
    type=str,
    required=True,
    help="Name of the route in the AI gateway",
)
def cli(read_file_path, overwrite, write_file_path, gateway_uri, gateway_route_name):
    """
    Execute a single file operation based on the given parameters and run type.
    """
    Run(
        read_file_path, overwrite, write_file_path, gateway_uri, gateway_route_name
    ).single_file_run()


if __name__ == "__main__":
    cli()
