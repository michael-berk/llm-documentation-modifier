from bs4 import BeautifulSoup
import click
import difflib
import pandas as pd
import os

DIRS_TO_NOT_SEARCH = {"/_modules/"}

def _get_relative_file_name(full_path: str) -> str:
    return full_path.split("mlflow")[-1].replace("/docs/build/html/", "")

def preprocess_lines(soup):
    soup = BeautifulSoup(soup.prettify(), "html.parser").get_text()
    lines = str(soup).splitlines(keepends=True)
    return lines

def diff_files(old_soup, new_soup):
    old_lines = preprocess_lines(old_soup)
    new_lines = preprocess_lines(new_soup)

    diff = difflib.ndiff(old_lines, new_lines)
    filtered_diff = [
        (i, line.rstrip("\n"))
        for i, line in enumerate(diff)
        if (line.startswith("- ") or line.startswith("+ ")) and len(line[1:].strip()) > 0
    ]

    return filtered_diff



def compare_html_files(old_dir: str, new_dir: str):
    paths_with_diffs = []
    for root, _, files in os.walk(old_dir):
        for file in files:
            if file.endswith(".html") and not any([d in root for d in DIRS_TO_NOT_SEARCH]):
                # print(_get_relative_file_name(root + '/' + file))
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


                        diff = diff_files(old_soup, new_soup)
                        if len(diff) > 0:
                            paths_with_diffs.append(new_file_path)
                            print(new_file_path)
                            print("------------------------------")

                            for x in diff:
                                print(f"{x[0]}: {x[1]}")

    print("\n"*5)
    print("List of all files with diffs:")
    print("------------------------------")
    for p in paths_with_diffs:
        print(p)


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
