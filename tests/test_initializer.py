# Copyright (C) 2023 twyleg
import sys
import unittest
import tempfile
import shutil
import logging

from pathlib import Path
from typing import List

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

    def prepare_template_project(self, dst_dir: Path) -> Path:
        dst_path = dst_dir / self.template_project_name
        shutil.copytree(self.template_project_path, dst_path, symlinks=False)
        return dst_path

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

    def setUp(self) -> None:
        logging.basicConfig(stream=sys.stdout, format=FORMAT, level=logging.DEBUG)
        self.output_dir_path = self.prepare_output_directory()
        self.test_project_path = self.prepare_template_project(self.output_dir_path)
        logging.info("Tmp working dir: %s", self.template_project_path)

    def tearDown(self):
        logging.shutdown()
        print("")


class CppTemplateInitializeTestCase(TemplateInitializeTestCase):
    def __init__(self, method_name="runTest"):
        super().__init__(method_name, "template_project_cpp")

    def test_TemplateCreated_Initialize_Success(self):
        init_template(self.test_project_path / "template_config.yaml", "target_string", dry_run=False)
        self.expect_no_occurrences_of_keywords(["template_project_cpp"])


class CppQtQmlTemplateInitializeTestCase(TemplateInitializeTestCase):
    def __init__(self, method_name="runTest"):
        super().__init__(method_name, "template_project_cpp_qt_qml")

    def test_TemplateCreated_Initialize_Success(self):
        init_template(self.test_project_path / "template_config.yaml", "target_string", dry_run=False)
        self.expect_no_occurrences_of_keywords(["template_project_cpp_qt_qml"])


class PythonTemplateInitializeTestCase(TemplateInitializeTestCase):
    def __init__(self, method_name="runTest"):
        super().__init__(method_name, "template_project_python")

    def test_TemplateCreated_Initialize_Success(self):
        init_template(self.test_project_path / "template_config.yaml", "target_string", dry_run=False)
        self.expect_no_occurrences_of_keywords(["template_project_python"])


class KicadTemplateInitializeTestCase(TemplateInitializeTestCase):
    def __init__(self, method_name="runTest"):
        super().__init__(method_name, "template_project_kicad")

    def test_TemplateCreated_Initialize_Success(self):
        init_template(self.test_project_path / "template_config.yaml", "target_string", dry_run=False)
        self.expect_no_occurrences_of_keywords(["template_project_kicad"])


if __name__ == "__main__":
    unittest.main()
