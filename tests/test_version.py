from importlib import metadata
from unittest.mock import patch

import pytest

from dot_tools.version import get_version, get_version_from_metadata, get_version_from_pyproject


class TestGetVersionFromMetadata:

    def test_get_version_from_metadata__returns_installed_version(self):
        with patch("dot_tools.version.metadata.version", return_value="1.2.3"):
            assert get_version_from_metadata() == "1.2.3"

    def test_get_version_from_metadata__raises_on_missing_package(self):
        with patch("dot_tools.version.metadata.version", side_effect=metadata.PackageNotFoundError):
            with pytest.raises(metadata.PackageNotFoundError):
                get_version_from_metadata()


class TestGetVersionFromPyproject:

    def test_get_version_from_pyproject__reads_version_from_file(self, tmp_path, monkeypatch):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nversion = "3.2.1"\n')

        monkeypatch.chdir(tmp_path)
        assert get_version_from_pyproject() == "3.2.1"

    def test_get_version_from_pyproject__raises_on_missing_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with pytest.raises(FileNotFoundError):
            get_version_from_pyproject()

    def test_get_version_from_pyproject__raises_on_missing_key(self, tmp_path, monkeypatch):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'fake'\n")

        monkeypatch.chdir(tmp_path)
        with pytest.raises(KeyError):
            get_version_from_pyproject()


class TestGetVersion:

    def test_get_version__returns_metadata_version_when_available(self):
        with patch("dot_tools.version.get_version_from_metadata", return_value="4.5.6"):
            assert get_version() == "4.5.6"

    def test_get_version__falls_back_to_pyproject_when_not_installed(self, tmp_path, monkeypatch):
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nversion = "0.1.0"\n')
        monkeypatch.chdir(tmp_path)

        with patch("dot_tools.version.get_version_from_metadata", side_effect=metadata.PackageNotFoundError):
            assert get_version() == "0.1.0"

    def test_get_version__returns_unknown_when_all_sources_fail(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        with patch("dot_tools.version.get_version_from_metadata", side_effect=metadata.PackageNotFoundError):
            assert get_version() == "unknown"
