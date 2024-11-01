from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict

import tomllib

DBX_REQUIREMENT_URL = "https://docs.databricks.com/en/_extras/documents/"


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

    @classmethod
    def complement_requirements(
        cls,
        first_requirement: "PythonRequirement",
        second_requirement: "PythonRequirement",
    ) -> Dict[str, str]:
        return {
            k: v
            for k, v in first_requirement._requirements.items()
            if k not in second_requirement._requirements.keys()
        }


class DBXPIPRequirement(PythonRequirement):
    def __init__(self, version: float):
        self.version = version

    def _create_requirement_url(self):
        return DBX_REQUIREMENT_URL + f"requirements-{self.version}.txt"

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
            self._requirements = dep_dict
            self._clean_version_strings()

    def _clean_version_strings(self):
        for k in self._requirements.keys():
            self._requirements[k] = self._requirements[k].replace("^", "")


class PoetryRequirement(PythonRequirement):
    def __init__(self):
        pass

    def load_requirement_file(self) -> None:
        pass
