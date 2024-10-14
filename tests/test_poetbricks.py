import pytest
import requests_mock

from pathlib import Path

from poetbricks.main import check_first_run, get_requirement_dict_from_server
from poetbricks import main


def test_check_first_run_correct(tmp_path: Path, monkeypatch, capfd):
    tmp_poetbircks_path = tmp_path / ".poetbricks"
    monkeypatch.setattr(main, "POETBRICKS_SETTINGS_ROOT_PATH", tmp_poetbircks_path)
    monkeypatch.setattr(
        main, "POETBRICKS_DBX_REQUIREMENT_PATH", tmp_poetbircks_path / "dbx_req"
    )
    check_first_run()

    out, _ = capfd.readouterr()
    assert "First run of poetbricks!" in out
    assert tmp_poetbircks_path.exists()
    assert (tmp_poetbircks_path / "dbx_req").exists()


def test_check_first_run_folder_already_exist(tmp_path: Path, monkeypatch, capfd):
    tmp_poetbircks_path = tmp_path / ".poetbricks"
    tmp_poetbircks_path.mkdir()
    tmp_bdx_path = tmp_poetbircks_path / "dbx_req"
    tmp_bdx_path.mkdir()

    monkeypatch.setattr(main, "POETBRICKS_SETTINGS_ROOT_PATH", tmp_poetbircks_path)
    monkeypatch.setattr(main, "POETBRICKS_DBX_REQUIREMENT_PATH", tmp_bdx_path)

    assert tmp_poetbircks_path.exists()
    assert (tmp_poetbircks_path / "dbx_req").exists()

    check_first_run()

    out, _ = capfd.readouterr()
    assert "First run of poetbricks!" not in out


@requests_mock.Mocker(kw="mock")
def test_get_requirement_dict_from_server(**kwargs):
    version = 15.3
    conent_data = b"tensorboard==2.16.2\ntorch==2.3.0+cpu\nrequests==2.32.4"
    kwargs["mock"].get(
        f"https://docs.databricks.com/en/_extras/documents/requirements-{version}.txt",
        content=conent_data,
    )
    req_dict = get_requirement_dict_from_server(version=version)

    assert list(req_dict.keys()) == ["tensorboard", "torch", "requests"]
    assert list(req_dict.values()) == ["2.16.2", "2.3.0+cpu", "2.32.4"]
