import shutil
from pathlib import Path

import pytest
import requests

from pandas_profiling.controller import console
from pandas_profiling.utils.paths import get_config_default


@pytest.fixture(scope="module")
def data_dir(tmpdir_factory):
    data_path = Path(str(tmpdir_factory.mktemp("test_console")))
    file_name = data_path / "rows.csv"
    if not file_name.exists():
        data = requests.get(
            "https://data.nasa.gov/api/views/gh4g-9sfh/rows.csv?accessType=DOWNLOAD"
        )
        file_name.write_bytes(data.content)
    yield data_path
    shutil.rmtree(str(data_path))


def test_console_multiprocessing(data_dir):
    report = data_dir / "test_samples.html"
    console.main(["-s", "--pool_size", "0", str(data_dir / "rows.csv"), str(report)])
    assert report.exists(), "Report should exist"


def test_console_single_core(data_dir):
    report = data_dir / "test_single_core.html"
    console.main(["-s", "--pool_size", "1", str(data_dir / "rows.csv"), str(report)])
    assert report.exists(), "Report should exist"


def test_console_minimal(data_dir):
    report = data_dir / "test_minimal.html"
    console.main(["-s", "--minimal", str(data_dir / "rows.csv"), str(report)])
    assert report.exists(), "Report should exist"


def test_double_config(data_dir):
    report = data_dir / "test_double_config.html"
    with pytest.raises(ValueError) as e:
        console.main(
            [
                "--config_file",
                str(get_config_default()),
                "--minimal",
                str(data_dir / "rows.csv"),
                str(report),
            ]
        )

    assert (
        str(e.value) == "Arguments `config_file` and `minimal` are mutually exclusive."
    )
