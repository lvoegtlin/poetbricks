from pathlib import Path

from poetbricks.requirements import PoetryRequirement, PythonRequirement


class Poetbricks:
    def __init__(self):
        pass

    @classmethod
    def from_project_file(cls, project_file_path: Path) -> PythonRequirement:
        return PoetryRequirement()
        pass

    def write_pip_requirement_file(self, output_path: Path) -> None:
        pass


if __name__ == "__main__":
    p = Poetbricks()
