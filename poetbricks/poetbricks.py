from pathlib import Path

from poetbricks.requirements import (
    DBXPIPRequirement,
    PoetryRequirement,
    PythonRequirement,
)


class Poetbricks:
    def __init__(self, dbx_req: DBXPIPRequirement, poetry_req: PoetryRequirement):
        self.dbx_req: DBXPIPRequirement = dbx_req
        self.poetry_req: PoetryRequirement = poetry_req

    @classmethod
    def from_project_file(cls, project_file_path: Path, version: float) -> "Poetbricks":
        dbx: DBXPIPRequirement = DBXPIPRequirement(version=version)
        poetry: PoetryRequirement = PoetryRequirement(file_path=project_file_path)

        dbx.load_requirement_file()
        poetry.load_requirement_file()

        return Poetbricks(dbx_req=dbx, poetry_req=poetry)

    def write_pip_requirement_file(self, output_path: Path, override: bool) -> None:
        complement = PythonRequirement.complement_requirements(
            source=self.poetry_req, check=self.dbx_req
        )
        print(complement)
        # PythonRequirement.save_complement_requirement_file(
        #    requirements=complement, output_path=output_path, override=override
        # )


if __name__ == "__main__":
    p = Poetbricks.from_project_file(Path("."), version=15.3)

    p.write_pip_requirement_file(Path("."), False)
