import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict

import requests
import tomllib

DBX_REQUIREMENT_URL = "https://docs.databricks.com/en/_extras/documents/"
POETBRICKS_SETTINGS_ROOT_PATH = Path("~/.poetbricks").expanduser()
POETBRICKS_DBX_REQUIREMENT_PATH = POETBRICKS_SETTINGS_ROOT_PATH / "dbx_req"

logger = logging.getLogger("requirements")


class PythonRequirement(ABC):
    def __init__(self):
        self._source_path: Path = Path("")
        self._requirements: Dict = {}

    @abstractmethod
    def load_requirement_file(self) -> None:
        pass

    @property
    def requirements(self) -> Dict:
        return self._requirements

    @requirements.setter
    def requirements(self, value: Dict[str, str]):
        self._requirements = value

    @property
    def source_path(self) -> Path:
        """doc"""
        return self._source_path

    @source_path.setter
    def source_path(self, value: Path):
        self._source_path = value

    @staticmethod
    def complement_requirements(
        source: "PythonRequirement",
        check: "PythonRequirement",
    ) -> Dict[str, str]:
        # TODO:return requirement pipfile object and not just a dict
        return {
            k: v
            for k, v in source.requirements.items()
            if k not in check.requirements.keys()
        }

    def save_complement_requirement_file(
        self, output_path: Path, override: bool
    ) -> None:
        requirement_file_path = output_path.parent / "requirements.txt"
        if requirement_file_path.exists() and override:
            raise ValueError(
                f"Requirement file exists in {output_path.parent} and override is not allowed!"
            )
        file_content_list = [f"{k}=={v}" for k, v in self.requirements.items()]
        with requirement_file_path.open("w") as f:
            f.write("\n".join(file_content_list))


class DBXPIPRequirement(PythonRequirement):
    def __init__(self, version: float):
        self.version = version

    def load_requirement_file(self) -> None:
        # check if file exists
        if self._check_dbx_file_exists():
            logger.info("DBX requirement file existing. Loading...")
            self.requirements = self._get_requirement_file()
            return

        self._get_requirement_dict_from_server()
        self._save_req_dict()

    def _get_requirement_file(self) -> Dict:
        file_path = POETBRICKS_DBX_REQUIREMENT_PATH / f"{self.version}.json"
        with file_path.open("r") as f:
            return json.load(f)

    def _create_requirement_url(self):
        return DBX_REQUIREMENT_URL + f"requirements-{self.version}.txt"

    def _check_dbx_file_exists(self) -> bool:
        return (POETBRICKS_DBX_REQUIREMENT_PATH / f"{self.version}.json").exists()

    def _save_req_dict(self) -> None:
        logger.info("Saving DBX requirements file...")
        with (POETBRICKS_DBX_REQUIREMENT_PATH / f"{self.version}.json").open("w") as f:
            json.dump(self.requirements, f)

    def _get_requirement_dict_from_server(self) -> None:
        logger.info("Downloading missing requirements file...")
        req_url = f"https://docs.databricks.com/en/_extras/documents/requirements-{self.version}.txt"

        req_file_request = requests.get(req_url, allow_redirects=True, timeout=5)
        req_file_content = req_file_request.content.decode("UTF-8")
        req_dict = {
            line.split("==")[0]: line.split("==")[1]
            for line in req_file_content.split("\n")
            if line != ""
        }
        self.requirements = req_dict


class PoetryRequirement(PythonRequirement):
    def __init__(self, file_path: Path):
        self._source_path: Path = file_path

    def load_requirement_file(self) -> None:
        toml_path: Path = self._source_path / "pyproject.toml"
        if not toml_path.exists():
            raise ValueError(
                f"No pyproject.toml file found in the given path ({self._source_path})"
            )

        with toml_path.open("rb") as toml_file:
            toml = tomllib.load(toml_file)

            dep_dict: Dict[str, Any] = toml["tool"]["poetry"]["dependencies"]
            del dep_dict["python"]
            self.requirements = dep_dict
            self._clean_version_strings()

    def _clean_version_strings(self):
        for k in self.requirements.keys():
            self.requirements[k] = self._requirements[k].replace("^", "")
