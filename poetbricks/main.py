import tomllib
import requests
from pathlib import Path
from argparse import ArgumentParser
import json
from typing import Dict, Any

POETBRICKS_SETTINGS_ROOT_PATH = Path("~/.poetbricks").expanduser()
POETBRICKS_DBX_REQUIREMENT_PATH = POETBRICKS_SETTINGS_ROOT_PATH / "dbx_req"


def main(toml_path: Path, databricks_version: float, not_overwrite_requirements: bool):
    # get dbx requirement list
    req_dict: Dict[str, str] = get_dbx_requirement_list(version=databricks_version)
    dep_dict: Dict[str, str] = get_toml_dependencies(path=toml_path)

    new_req = complement_dependencies_and_requirements(
        dbx_dependencies=req_dict, dependencies=dep_dict
    )

    # write new requirements file
    save_complement_requirement_file(
        requirements=new_req, toml_path=toml_path, override=not_overwrite_requirements
    )


def save_complement_requirement_file(
    requirements: Dict[str, str], toml_path: Path, override: bool
) -> None:
    requirement_file_path = toml_path.parent / "requirements.txt"
    if requirement_file_path.exists() and override:
        raise ValueError(
            f"Requirement file exists in {toml_path.parent} and override is not allowed!"
        )
    file_content_list = [f"{k}=={v}" for k, v in requirements.items()]
    with requirement_file_path.open("w") as f:
        f.write("\n".join(file_content_list))


def complement_dependencies_and_requirements(
    dbx_dependencies: Dict[str, str], dependencies: Dict[str, str]
) -> Dict[str, str]:
    return {
        k: v.replace("^", "")
        for k, v in dependencies.items()
        if k not in dbx_dependencies.keys()
    }


def get_toml_dependencies(path: Path) -> Dict[str, str]:
    toml_path: Path = path / "pyproject.toml"
    if not toml_path.exists():
        raise ValueError(f"No pyproject.toml file found in the given path ({path})")

    with toml_path.open("rb") as toml_file:
        toml = tomllib.load(toml_file)

        dep_dict: Dict[str, Any] = toml["tool"]["poetry"]["dependencies"]
        del dep_dict["python"]
        return dep_dict


def check_dbx_file_exists(version: float) -> bool:
    return (POETBRICKS_DBX_REQUIREMENT_PATH / f"{version}.json").exists()


def get_requirement_file(version: float) -> Dict:
    file_path = POETBRICKS_DBX_REQUIREMENT_PATH / f"{version}.json"
    with file_path.open("r") as f:
        return json.load(f)


def get_dbx_requirement_list(version: float) -> Dict[str, str]:
    # check if file exists
    if check_dbx_file_exists(version=version):
        return get_requirement_file(version=version)

    req_dict = get_dbx_requirement_list(version=version)
    save_req_dict(req_dict=req_dict, version=version)

    return req_dict


def save_req_dict(req_dict: Dict[str, str], version: float) -> None:
    with (POETBRICKS_DBX_REQUIREMENT_PATH / f"{version}.json").open("w") as f:
        json.dump(req_dict, f)


def get_requirement_dict_from_server(version: float) -> Dict[str, str]:
    req_url = (
        f"https://docs.databricks.com/en/_extras/documents/requirements-{version}.txt"
    )

    req_file_request = requests.get(req_url, allow_redirects=True)
    req_file_content = req_file_request.content.decode("UTF-8")
    req_dict = {
        line.split("==")[0]: line.split("==")[1]
        for line in req_file_content.split("\n")
    }
    return req_dict


def check_first_run() -> None:
    if not POETBRICKS_SETTINGS_ROOT_PATH.exists():
        print("First run of poetbricks!")
        POETBRICKS_SETTINGS_ROOT_PATH.mkdir()
        POETBRICKS_DBX_REQUIREMENT_PATH.mkdir()


def entry() -> None:
    parser = ArgumentParser()
    parser.add_argument(
        "-i",
        "--toml_path",
        type=Path,
        default=".",
        help="Path to the pyproject.toml file you want to parse the requirements from. The newly created requirements.txt file will be added to the folder containing pyproject.toml.",
    )
    parser.add_argument(
        "-v",
        "--databricks_version",
        required=True,
        type=float,
        help="Version of the DBX compute cluster. (e.g., 15.3 for the 15.3LTS)",
    )
    parser.add_argument(
        "-w",
        "--not_overwrite_requirements",
        action="store_true",
        help="If set does not override existing requirements.txt file in the pyproject.toml folder.",
    )

    check_first_run()
    args = parser.parse_args()

    main(**args.__dict__)


if __name__ == "__main__":
    entry()
