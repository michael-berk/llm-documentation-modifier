import click
from llm_documentation_modifier.run import Run


@click.command()
@click.option(
    "--read-file-path",
    type=str,
    required=True,
    help=(
        "Path to the file with source docstrings. If a directory is specified, the program will"
        "iterate over all files in the dir."
    ),
)
@click.option(
    "--write-file-path",
    type=str,
    required=False,
    default=None,
    help=(
        "Path to the file where transformed lines will be written. If no write path is specified,"
        "the read file path will be overwritten."
    ),
)
@click.option(
    "--deploy-uri",
    type=str,
    required=False,
    default="http://localhost:5000",
    help="URI for the mlflow deploy URI serving the LLM",
)
@click.option(
    "--deploy-route-name",
    type=str,
    required=True,
    help="Name of the route in the AI deploy",
)
def cli(read_file_path, write_file_path, deploy_uri, deploy_route_name):
    """
    Execute a single file operation based on the given parameters and run type.
    """
    Run(read_file_path, write_file_path, deploy_uri, deploy_route_name).run()


if __name__ == "__main__":
    cli()
