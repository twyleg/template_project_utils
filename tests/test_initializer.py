# Copyright (C) 2024 twyleg
# fmt: off
import shutil
import sys
from typing import List

import pygit2
import pytest
from _pytest.monkeypatch import MonkeyPatch

from pathlib import Path

from template_project_utils.template_initializer import TemplateInitializer


FILE_DIR = Path(__file__).parent


def prepare_test_project_git_repo(test_project_path: Path) -> None:
    git_file_from_submodule = test_project_path / ".git"
    git_file_from_submodule.unlink()

    test_project_name = test_project_path.name
    test_project_dummy_remote_url = f"git@github.com:twyleg/{test_project_name}.git"
    test_project_repo = pygit2.init_repository(test_project_path, False)
    test_project_repo.remotes.create("origin", test_project_dummy_remote_url)


def create_test_project_from_template_and_chdir(template_project_src_dir_path: Path,
                                                template_project_dst_dir_path: Path,
                                                monkeypatch: MonkeyPatch) -> Path:
    template_project_dst_dir_path = template_project_dst_dir_path / template_project_src_dir_path.name
    shutil.copytree(template_project_src_dir_path, template_project_dst_dir_path)
    monkeypatch.chdir(template_project_dst_dir_path)
    prepare_test_project_git_repo(template_project_dst_dir_path)
    return template_project_dst_dir_path


@pytest.fixture
def template_project_cpp_master(tmp_path, monkeypatch):
    return create_test_project_from_template_and_chdir(
        FILE_DIR / "../external/template_project_cpp_master",
        tmp_path,
        monkeypatch
    )


@pytest.fixture
def template_project_cpp_usecase_qt_qml_app(tmp_path, monkeypatch):
    return create_test_project_from_template_and_chdir(
        FILE_DIR / "../external/template_project_cpp_usecase_qt_qml_app",
        tmp_path,
        monkeypatch
    )


@pytest.fixture
def template_project_kicad_master(tmp_path, monkeypatch):
    return create_test_project_from_template_and_chdir(
        FILE_DIR / "../external/template_project_kicad_master",
        tmp_path,
        monkeypatch
    )


@pytest.fixture
def template_project_python_master(tmp_path, monkeypatch):
    return create_test_project_from_template_and_chdir(
        FILE_DIR / "../external/template_project_python_master",
        tmp_path,
        monkeypatch
    )


@pytest.fixture
def template_project_python_usecase_qt_qml_app(tmp_path, monkeypatch):
    return create_test_project_from_template_and_chdir(
        FILE_DIR / "../external/template_project_python_usecase_qt_qml_app",
        tmp_path,
        monkeypatch
    )


def is_git_remote_origin_still_available(test_project_path: Path) -> bool:
    repo = pygit2.Repository(str(test_project_path))
    remote_collection = pygit2.remotes.RemoteCollection(repo)
    return "origin" in remote_collection.names()


def is_any_placeholder_still_available(test_project_path: Path, keywords: List[str]):
    file_name_count = 0
    dir_name_count = 0
    file_content_count = 0

    for path in test_project_path.rglob("*"):
        if path.is_relative_to(test_project_path / ".git/"):
            pass  # Ignore
        elif path.is_relative_to(test_project_path / "venv/"):
            pass  # Ignore
        elif path.is_relative_to(test_project_path / "logs/"):
            pass  # Ignore
        elif path.is_dir():
            relative_path = str(path.relative_to(test_project_path))
            for keyword in keywords:
                if keyword in relative_path:
                    dir_name_count += 1
                    print(f"Error: Keyword \"{keyword}\" found in directory name \"{relative_path}\"", file=sys.stderr)
        elif path.is_file():
            relative_path = str(path.relative_to(test_project_path))
            for keyword in keywords:
                if keyword in relative_path:
                    file_name_count += 1
                    print(f"Error: Keyword \"{keyword}\" found in file name \"{relative_path}\"", file=sys.stderr)

            try:
                content = path.read_text()
                for keyword in keywords:
                    count = content.count(keyword)
                    file_content_count += count
                    if count:
                        print(f"Error: Keyword \"{keyword}\" found {count} times in file \"{path}\"", file=sys.stderr)
            except UnicodeDecodeError as e:
                pass
    return file_name_count > 0 or dir_name_count > 0 or file_content_count > 0


def is_project_correctly_initialized(test_project_path: Path, template_project_keywords: List[str]) -> bool:
    if is_any_placeholder_still_available(test_project_path, template_project_keywords):
        return False
    elif is_git_remote_origin_still_available(test_project_path):
        return False
    return True


class TestInitializer:
    def test_ValidTemplateProjectCppMaster_InitializeTemplate_InitializationSuccessful(self, template_project_cpp_master):
        template_initializer = TemplateInitializer(template_project_cpp_master / "template_config.yaml")
        template_initializer.init({"template_project_cpp": "test_target_name"})
        assert is_project_correctly_initialized(template_project_cpp_master, ["template_project_cpp"])

    def test_ValidTemplateProjectCppUsecaseQtQmlApp_InitializeTemplate_InitializationSuccessful(self, template_project_cpp_usecase_qt_qml_app):
        template_initializer = TemplateInitializer(template_project_cpp_usecase_qt_qml_app / "template_config.yaml")
        template_initializer.init({"template_project_cpp": "test_target_name"})
        assert is_project_correctly_initialized(template_project_cpp_usecase_qt_qml_app, ["template_project_cpp"])

    def test_ValidTemplateProjectKicadMaster_InitializeTemplate_InitializationSuccessful(self, template_project_kicad_master):
        template_initializer = TemplateInitializer(template_project_kicad_master / "template_config.yaml")
        template_initializer.init({"template_project_kicad": "test_target_name"})
        assert is_project_correctly_initialized(template_project_kicad_master, ["template_project_kicad"])

    def test_ValidTemplateProjectPythonMaster_InitializeTemplate_InitializationSuccessful(self, template_project_python_master):
        template_initializer = TemplateInitializer(template_project_python_master / "template_config.yaml")
        template_initializer.init({
            "template_project_python": "test_target_name",
            "template-project-python": "test-target-name",
        })
        assert is_project_correctly_initialized(template_project_python_master, ["template_project_python"])

    def test_ValidTemplateProjectPythonUsecaseQtQmlApp_InitializeTemplate_InitializationSuccessful(self, template_project_python_usecase_qt_qml_app):
        template_initializer = TemplateInitializer(template_project_python_usecase_qt_qml_app / "template_config.yaml")
        template_initializer.init({
            "template_project_python": "test_target_name",
            "template-project-python": "test-target-name",
        })
        assert is_project_correctly_initialized(template_project_python_usecase_qt_qml_app, ["template_project_python"])
