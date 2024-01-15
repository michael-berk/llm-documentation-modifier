from bs4 import BeautifulSoup
import click
import difflib
import pandas as pd
import os


def diff_files(old_soup, new_soup):
    # Prettify to format then text text
    old_soup = BeautifulSoup(old_soup.prettify(), "html.parser").get_text()
    new_soup = BeautifulSoup(new_soup.prettify(), "html.parser").get_text()

    diff = difflib.ndiff(
        str(old_soup).splitlines(keepends=True), str(new_soup).splitlines(keepends=True)
    )

    filtered_diff = [
        (i, line.rstrip("\n"))
        for i, line in enumerate(diff)
        if (line.startswith("- ") or line.startswith("+ ")) and line.strip() != ""
    ]

    for x in filtered_diff:
        print(f"{x[0]}: {x[1]}")


def compare_html_files(old_dir: str, new_dir: str):
    for root, _, files in os.walk(old_dir):
        for file in files:
            if file.endswith(".html"):
                print(file)
                print("------------------------------")
                old_file_path = os.path.join(root, file)
                new_file_path = os.path.join(
                    new_dir, os.path.relpath(old_file_path, old_dir)
                )

                if os.path.exists(new_file_path):
                    with open(old_file_path, "r") as old_file, open(
                        new_file_path, "r"
                    ) as new_file:
                        old_soup = BeautifulSoup(old_file.read(), "html.parser")
                        new_soup = BeautifulSoup(new_file.read(), "html.parser")

                        diff_files(old_soup, new_soup)


@click.command()
@click.option(
    "--old_commit_path",
    required=True,
    help="Path to the rendered html docs for the commit prior to your changes.",
)
@click.option(
    "--new_commit_path",
    required=True,
    help="Path to the rendered html docs for the commit with your newest commit.",
)
def main(old_commit_path, new_commit_path):
    return compare_html_files(old_commit_path, new_commit_path)


if __name__ == "__main__":
    main()
