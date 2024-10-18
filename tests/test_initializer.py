# Copyright (C) 2024 twyleg
# fmt: off
import os
import shutil
import sys
from collections import namedtuple
from dataclasses import dataclass
from typing import Dict, Any


import pygit2
import pytest
import yaml
from _pytest.monkeypatch import MonkeyPatch

from pathlib import Path

from template_project_utils.template_initializer import TemplateInitializer


FILE_DIR = Path(__file__).parent


@dataclass
class TestProject:
    path: Path
    config: Dict[str, Any]
    placeholder_target_pairs: Dict[str, str]


def prepare_test_project_git_repo(test_project_path: Path) -> None:
    git_file_from_submodule = test_project_path / ".git"
    git_file_from_submodule.unlink()

    test_project_name = test_project_path.name
    test_project_dummy_remote_url = f"git@github.com:twyleg/{test_project_name}.git"
    test_project_repo = pygit2.init_repository(test_project_path, False)
    test_project_repo.remotes.create("origin", test_project_dummy_remote_url)


def read_template_config(test_project_config_file_path: Path) -> Dict[str, Any]:
    with open(test_project_config_file_path, "r") as file:
        return yaml.safe_load(file)


def create_test_project_from_template_and_chdir(template_project_src_dir_path: Path,
                                                template_project_dst_dir_path: Path,
                                                template_project_config_filename: str,
                                                template_project_placeholder_target_pairs: Dict[str, str],
                                                monkeypatch: MonkeyPatch,
                                                ) -> TestProject:
    template_project_dst_dir_path = template_project_dst_dir_path / template_project_src_dir_path.name
    shutil.copytree(template_project_src_dir_path, template_project_dst_dir_path)
    monkeypatch.chdir(template_project_dst_dir_path)
    prepare_test_project_git_repo(template_project_dst_dir_path)
    template_project_config = read_template_config(template_project_dst_dir_path / template_project_config_filename)

    return TestProject(
        path=template_project_dst_dir_path,
        config=template_project_config,
        placeholder_target_pairs=template_project_placeholder_target_pairs
    )


@pytest.fixture
def template_project_cpp_master(tmp_path, monkeypatch):
    return create_test_project_from_template_and_chdir(
        template_project_src_dir_path=FILE_DIR / "../external/template_project_cpp_master",
        template_project_dst_dir_path=tmp_path,
        template_project_config_filename="template_config.yaml",
        template_project_placeholder_target_pairs={"template_project_cpp": "test_target_name"},
        monkeypatch=monkeypatch
    )


@pytest.fixture
def template_project_cpp_usecase_qt_qml_app(tmp_path, monkeypatch):
    return create_test_project_from_template_and_chdir(
        template_project_src_dir_path=FILE_DIR / "../external/template_project_cpp_usecase_qt_qml_app",
        template_project_dst_dir_path=tmp_path,
        template_project_config_filename="template_config.yaml",
        template_project_placeholder_target_pairs={"template_project_cpp": "test_target_name"},
        monkeypatch=monkeypatch
    )


@pytest.fixture
def template_project_kicad_master(tmp_path, monkeypatch):
    return create_test_project_from_template_and_chdir(
        template_project_src_dir_path=FILE_DIR / "../external/template_project_kicad_master",
        template_project_dst_dir_path=tmp_path,
        template_project_config_filename="template_config.yaml",
        template_project_placeholder_target_pairs={"template_project_kicad": "test_target_name"},
        monkeypatch=monkeypatch
    )


@pytest.fixture
def template_project_python_master(tmp_path, monkeypatch):
    return create_test_project_from_template_and_chdir(
        template_project_src_dir_path=FILE_DIR / "../external/template_project_python_master",
        template_project_dst_dir_path=tmp_path,
        template_project_config_filename="template_config.yaml",
        template_project_placeholder_target_pairs={
            "template_project_python": "test_target_name",
            "template-project-python": "test-target-name",
        },
        monkeypatch=monkeypatch
    )


@pytest.fixture
def template_project_python_master_with_alternative_config_filename(template_project_python_master):
    old_config_file_name = template_project_python_master.path / "template_config.yaml"
    new_config_file_name = template_project_python_master.path / "template_config_alt.yaml"
    os.rename(old_config_file_name, new_config_file_name)
    new_config_file_name.write_text(new_config_file_name.read_text().replace("- template_config.yaml", "- template_config_alt.yaml"))
    return template_project_python_master


@pytest.fixture
def template_project_python_usecase_qt_qml_app(tmp_path, monkeypatch):
    return create_test_project_from_template_and_chdir(
        template_project_src_dir_path=FILE_DIR / "../external/template_project_python_usecase_qt_qml_app",
        template_project_dst_dir_path=tmp_path,
        template_project_config_filename="template_config.yaml",
        template_project_placeholder_target_pairs={"template_project_python": "test_target_name"},
        monkeypatch=monkeypatch
    )


def is_git_remote_origin_still_existing(test_project: TestProject) -> bool:
    repo = pygit2.Repository(str(test_project.path))
    remote_collection = pygit2.remotes.RemoteCollection(repo)
    return "origin" in remote_collection.names()


def is_any_placeholder_still_existing(test_project: TestProject):
    file_name_count = 0
    dir_name_count = 0
    file_content_count = 0

    for path in test_project.path.rglob("*"):
        if path.is_relative_to(test_project.path / ".git/"):
            pass  # Ignore
        elif path.is_relative_to(test_project.path / "venv/"):
            pass  # Ignore
        elif path.is_relative_to(test_project.path / "logs/"):
            pass  # Ignore
        elif path.is_dir():
            relative_path = str(path.relative_to(test_project.path))
            for placeholder in test_project.placeholder_target_pairs.keys():
                if placeholder in relative_path:
                    dir_name_count += 1
                    print(f"Error: Placeholder \"{placeholder}\" found in directory name \"{relative_path}\"", file=sys.stderr)
        elif path.is_file():
            relative_path = str(path.relative_to(test_project.path))
            for placeholder in test_project.placeholder_target_pairs.keys():
                if placeholder in relative_path:
                    file_name_count += 1
                    print(f"Error: Placeholder \"{placeholder}\" found in file name \"{relative_path}\"", file=sys.stderr)

            try:
                content = path.read_text()
                for placeholder in test_project.placeholder_target_pairs.keys():
                    count = content.count(placeholder)
                    file_content_count += count
                    if count:
                        print(f"Error: Placeholder \"{placeholder}\" found {count} times in file \"{path}\"", file=sys.stderr)
            except UnicodeDecodeError as e:
                pass
    return file_name_count > 0 or dir_name_count > 0 or file_content_count > 0


def is_any_file_diff_not_plausible(test_project: TestProject) -> bool:
    if test_project.config["update_files"]:
        for update_file_name in test_project.config["update_files"]:

            for placeholder, target in test_project.placeholder_target_pairs.items():
                update_file_name = update_file_name.replace(placeholder, target)

            update_file_path = test_project.path / update_file_name
            if update_file_path.stat().st_size == 0:
                return True
    return False


def is_any_remove_file_candidate_still_existing(test_project: TestProject) -> bool:
    if test_project.config["remove_files"]:
        for remove_file_name in test_project.config["remove_files"]:
            remove_file_path = test_project.path / remove_file_name
            if remove_file_path.exists():
                return True
    return False


def is_any_remove_dir_candidate_still_existing(test_project: TestProject) -> bool:
    if test_project.config["remove_dirs"]:
        for remove_dir_name in test_project.config["remove_dirs"]:
            remove_dir_path = test_project.path / remove_dir_name
            if remove_dir_path.exists():
                return True
    return False


def is_any_rename_file_candidate_still_existing(test_project: TestProject) -> bool:
    if test_project.config["rename_files"]:
        for rename_file_name in test_project.config["rename_files"]:
            rename_file_path = test_project.path / rename_file_name
            if rename_file_path.exists():
                return True
    return False


def is_any_rename_dir_candidate_still_existing(test_project: TestProject) -> bool:
    if test_project.config["rename_dirs"]:
        for rename_dir_name in test_project.config["rename_dirs"]:
            rename_dir_path = test_project.path / rename_dir_name
            if rename_dir_path.exists():
                return True
    return False


def assert_project_correctly_initialized(test_project: TestProject) -> None:
    assert not is_any_placeholder_still_existing(test_project)
    assert not is_any_file_diff_not_plausible(test_project)
    assert not is_any_rename_file_candidate_still_existing(test_project)
    assert not is_any_rename_dir_candidate_still_existing(test_project)
    assert not is_any_remove_file_candidate_still_existing(test_project)
    assert not is_any_remove_dir_candidate_still_existing(test_project)
    assert not is_git_remote_origin_still_existing(test_project)


class TestInitializerForAllTemplateTypes:
    def test_ValidTemplateProjectCppMaster_InitializeTemplate_InitializationSuccessful(self, template_project_cpp_master):
        template_initializer = TemplateInitializer(template_project_cpp_master.path)
        template_initializer.init({"template_project_cpp": "test_target_name"})
        assert_project_correctly_initialized(template_project_cpp_master)

    def test_ValidTemplateProjectCppUsecaseQtQmlApp_InitializeTemplate_InitializationSuccessful(self, template_project_cpp_usecase_qt_qml_app):
        template_initializer = TemplateInitializer(template_project_cpp_usecase_qt_qml_app.path)
        template_initializer.init({"template_project_cpp": "test_target_name"})
        assert_project_correctly_initialized(template_project_cpp_usecase_qt_qml_app)

    def test_ValidTemplateProjectKicadMaster_InitializeTemplate_InitializationSuccessful(self, template_project_kicad_master):
        template_initializer = TemplateInitializer(template_project_kicad_master.path)
        template_initializer.init({"template_project_kicad": "test_target_name"})
        assert_project_correctly_initialized(template_project_kicad_master)

    def test_ValidTemplateProjectPythonMaster_InitializeTemplate_InitializationSuccessful(self, template_project_python_master):
        template_initializer = TemplateInitializer(template_project_python_master.path)
        template_initializer.init({
            "template_project_python": "test_target_name",
            "template-project-python": "test-target-name",
        })
        assert_project_correctly_initialized(template_project_python_master)

    def test_ValidTemplateProjectPythonUsecaseQtQmlApp_InitializeTemplate_InitializationSuccessful(self, template_project_python_usecase_qt_qml_app):
        template_initializer = TemplateInitializer(template_project_python_usecase_qt_qml_app.path)
        template_initializer.init({
            "template_project_python": "test_target_name",
            "template-project-python": "test-target-name",
        })
        assert_project_correctly_initialized(template_project_python_usecase_qt_qml_app)


class TestInitializerDetails:

    def test_ValidTemplateProjectPythonMasterWithCustomTemplateConfigFilename_InitializeTemplate_InitializationSuccessful(
            self,
            template_project_python_master_with_alternative_config_filename
    ):
        template_initializer = TemplateInitializer(template_project_python_master_with_alternative_config_filename.path / "template_config_alt.yaml")
        template_initializer.init({
            "template_project_python": "test_target_name",
            "template-project-python": "test-target-name",
        })
        assert_project_correctly_initialized(template_project_python_master_with_alternative_config_filename)

    def test_ValidTemplateProjectPythonMasterWithInvalidConfigFileNameParameter_InitializeTemplate_RuntimeErrorRaised(
            self,
            template_project_python_master
    ):
        with pytest.raises(RuntimeError):
            TemplateInitializer(template_project_python_master.path / "template_config_not_existing.yaml")

    def test_ValidTemplateProjectPythonMasterWithInvalidWorkingDirParameter_InitializeTemplate_RuntimeErrorRaised(
            self,
            template_project_python_master
    ):
        with pytest.raises(RuntimeError):
            TemplateInitializer(
                config_file_or_dir_path=template_project_python_master.path / "template_config.yaml",
                working_dir_path=Path("/not/existing/working/dir")
            )
