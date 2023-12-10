# Copyright (C) 2023 twyleg
import sys
import unittest
import tempfile
import shutil
import logging

from pathlib import Path
from template_project_utils.initializer import init_template

FORMAT = "[%(asctime)s][%(levelname)s][%(name)s]: %(message)s"
FILE_DIR = Path(__file__).parent

#
# General naming convention for unit tests:
#               test_INITIALSTATE_ACTION_EXPECTATION
#


class TemplateInitializeTestCase(unittest.TestCase):
    @classmethod
    def prepare_output_directory(cls) -> Path:
        tmp_dir = tempfile.mkdtemp()
        return Path(tmp_dir)

    def setUp(self) -> None:
        logging.basicConfig(stream=sys.stdout, format=FORMAT, level=logging.DEBUG)
        self.output_dir_path = self.prepare_output_directory()
        logging.info("Tmp working dir: %s", self.output_dir_path)

    def tearDown(self):
        logging.shutdown()
        print("")


class PythonTemplateInitializeTestCase(TemplateInitializeTestCase):
    TEMPLATE_PROJECT_PYTHON_DIR = FILE_DIR / "../external/template_project_python"

    @classmethod
    def prepare_template_project_python(cls, dst_dir: Path) -> Path:
        dst_path = dst_dir / "template_project_python"
        shutil.copytree(cls.TEMPLATE_PROJECT_PYTHON_DIR, dst_path)
        return dst_path

    def test_TemplateCreated_Initialize_Success(self):
        test_project_path = self.prepare_template_project_python(self.output_dir_path)
        init_template(test_project_path / "template_config.yaml", "target_string", dry_run=False)


class KicadTemplateInitializeTestCase(TemplateInitializeTestCase):
    TEMPLATE_PROJECT_KICAD_DIR = FILE_DIR / "../external/template_project_kicad"

    @classmethod
    def prepare_template_project_kicad(cls, dst_dir: Path) -> Path:
        dst_path = dst_dir / "template_project_kicad"
        shutil.copytree(cls.TEMPLATE_PROJECT_KICAD_DIR, dst_path, symlinks=False)
        return dst_path

    def test_TemplateCreated_Initialize_Success(self):
        test_project_path = self.prepare_template_project_kicad(self.output_dir_path)
        init_template(test_project_path / "template_config.yaml", "target_string", dry_run=False)


if __name__ == "__main__":
    unittest.main()
