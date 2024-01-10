# Copyright (C) 2023 twyleg
import sys
import unittest
import tempfile
import shutil
import logging

from pathlib import Path
from typing import List

import pygit2

from template_project_utils.initializer import init_template

FORMAT = "[%(asctime)s][%(levelname)s][%(name)s]: %(message)s"
FILE_DIR = Path(__file__).parent

#
# General naming convention for unit tests:
#               test_INITIALSTATE_ACTION_EXPECTATION
#


class TemplateInitializeTestCase(unittest.TestCase):
    def __init__(self, method_name: str, template_project_name: str):
        super().__init__(method_name)
        self.template_project_name = template_project_name
        self.template_project_path = FILE_DIR / f"../external/{template_project_name}"

    @classmethod
    def prepare_output_directory(cls) -> Path:
        tmp_dir = tempfile.mkdtemp()
        return Path(tmp_dir)

    @classmethod
    def prepare_test_project(cls, template_project_path: Path, dst_dir: Path) -> Path:
        test_project_name = template_project_path.name
        test_project_path = dst_dir / test_project_name
        shutil.copytree(template_project_path, test_project_path, symlinks=False)
        return test_project_path

    @classmethod
    def prepare_test_project_git_repo(cls, test_project_path: Path):
        git_file_from_submodule = test_project_path / ".git"
        git_file_from_submodule.unlink()

        test_project_name = test_project_path.name
        test_project_dummy_remote_url = f"git@github.com:twyleg/{test_project_name}.git"
        test_project_repo = pygit2.init_repository(test_project_path, False)
        test_project_repo.remotes.create("origin", test_project_dummy_remote_url)

    def expect_no_git_remote_origin(self):
        repo = pygit2.Repository(self.test_project_path)
        remote_collection = pygit2.remote.RemoteCollection(repo)
        with self.assertRaises(KeyError, msg="Remote 'origin' still existing."):
            remote_collection["origin"]

    def expect_no_occurrences_of_keywords(self, keywords: List[str]):
        dir_name_count = 0
        file_content_count = 0

        for path in self.test_project_path.rglob("*"):
            if path.is_relative_to(self.test_project_path / ".git/"):
                pass  # Ignore
            elif path.is_relative_to(self.test_project_path / "venv/"):
                pass  # Ignore
            elif path.is_dir():
                for keyword in keywords:
                    if keyword in str(path.relative_to(self.test_project_path)):
                        dir_name_count += 1
                        logging.debug("Dir path containing keyword '%s': %s", keyword, path)
            elif path.is_file():
                try:
                    content = path.read_text()
                    for keyword in keywords:
                        count = content.count(keyword)
                        file_content_count += count
                        if count:
                            logging.debug("File containing keyword '%s': %s", keyword, path)
                except UnicodeDecodeError as e:
                    pass
        self.assertEqual(0, dir_name_count)
        self.assertEqual(0, file_content_count)

    def expect_project_initialized_correctly(self):
        self.expect_no_occurrences_of_keywords([self.template_project_name])
        self.expect_no_git_remote_origin()

    def setUp(self) -> None:
        logging.basicConfig(stream=sys.stdout, format=FORMAT, level=logging.DEBUG)
        self.output_dir_path = self.prepare_output_directory()
        self.test_project_path = self.prepare_test_project(self.template_project_path, self.output_dir_path)
        self.prepare_test_project_git_repo(self.test_project_path)
        logging.info("Template project dir: %s", self.template_project_path)
        logging.info("Tmp test project dir: %s", self.test_project_path)

    def tearDown(self):
        logging.shutdown()
        print("")


class CppTemplateInitializeTestCase(TemplateInitializeTestCase):
    def __init__(self, method_name="runTest"):
        super().__init__(method_name, "template_project_cpp")

    def test_TemplateCreated_Initialize_Success(self):
        init_template(self.test_project_path / "template_config.yaml", "target_string", dry_run=False)
        self.expect_project_initialized_correctly()


class CppQtQmlTemplateInitializeTestCase(TemplateInitializeTestCase):
    def __init__(self, method_name="runTest"):
        super().__init__(method_name, "template_project_cpp_qt_qml")

    def test_TemplateCreated_Initialize_Success(self):
        init_template(self.test_project_path / "template_config.yaml", "target_string", dry_run=False)
        self.expect_project_initialized_correctly()


class PythonTemplateInitializeTestCase(TemplateInitializeTestCase):
    def __init__(self, method_name="runTest"):
        super().__init__(method_name, "template_project_python")

    def test_TemplateCreated_Initialize_Success(self):
        init_template(self.test_project_path / "template_config.yaml", "target_string", dry_run=False)
        self.expect_project_initialized_correctly()


class KicadTemplateInitializeTestCase(TemplateInitializeTestCase):
    def __init__(self, method_name="runTest"):
        super().__init__(method_name, "template_project_kicad")

    def test_TemplateCreated_Initialize_Success(self):
        init_template(self.test_project_path / "template_config.yaml", "target_string", dry_run=False)
        self.expect_project_initialized_correctly()


if __name__ == "__main__":
    unittest.main()
