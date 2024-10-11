import tomllib
from pathlib import Path
from argparse import ArgumentParser


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "-i",
        "--toml_path",
        required=True,
        type=Path,
        help="PAth to the pyproject.toml file you want to parse the requirements from.",
    )

    with toml_path.open("r") as toml:
        toml = tomllib.load(toml)
