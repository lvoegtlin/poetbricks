# poetbricks
A CLI tool to create requirements files that are compatible with databricks from the peorty section of the pypjroject.toml file.

## Requirements
- python >= 3.10
- requests >= 2.32.2

### Testing requirements
- request-mock >= 1.12.1
- pytest-mock >=3.14.0
- pytest >= 8.3.3

## Installation
We recommand to use pipx to install the package as follows:
```
pipx install poetbricks
```

But its also possible to use pip:

```
pip install poetbricks
```
## Usage
Run the `poetbricks` command inside of your `poetry` project. You need to provede the `-v` Databricks vmimage version. `poetbricks` will look for the `pyproject.toml` file in the current working directory if the argument `-i` is not set (pointing to the folder containig the `pyproject.toml` file). 

### Example
Create the `requirement.txt` file based on the Databricks 15.3 vmimage version and the pyproject toml.

```
poetbricks -v 15.3 -i . -w
```
The `-w` prevents `poetbricks` to override a `requirements.txt` file in `-i`.

### Running Tests
To run the tests use `poetry` to install all needed dependencies and run the tests.
``` 
poetry run pytest -v
```

## Contribute
If you find any problems or have feature requests create an issue or a PR.
