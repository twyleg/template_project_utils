# Copyright (C) 2023 twyleg
import sys
import unittest
import tempfile
import shutil
import logging

from pathlib import Path
from template_project_utils.initializer import init_template

FILE_DIR = Path(__file__).parent

TEMPLATE_PROJECT_PYTHON_DIR = FILE_DIR / "../external/template_project_python"


FORMAT = "[%(asctime)s][%(levelname)s][%(name)s]: %(message)s"
FILE_DIR = Path(__file__).parent

#
# General naming convention for unit tests:
#               test_INITIALSTATE_ACTION_EXPECTATION
#

class ExampleTestCase(unittest.TestCase):
    @classmethod
    def prepare_output_directory(cls) -> Path:
        tmp_dir = tempfile.mkdtemp()
        return Path(tmp_dir)

    @classmethod
    def prepare_template_project_python(cls, dst_dir: Path) -> Path:
        dst_path = dst_dir / "template_project_python"
        shutil.copytree(TEMPLATE_PROJECT_PYTHON_DIR, dst_path)
        return dst_path

    def setUp(self) -> None:
        logging.basicConfig(stream=sys.stdout, format=FORMAT, level=logging.DEBUG)
        self.output_dir_path = self.prepare_output_directory()
        print(self.output_dir_path)

    def tearDown(self):
        logging.shutdown()
        print("")

    def test_ArrangedState_Action_Assertion(self):
        config_filepath = self.output_dir_path / "template_config.yaml"
        # shutil.copyfile(FILE_DIR / "resources/test_config_0.yaml", config_filepath)

        test_project_path = self.prepare_template_project_python(self.output_dir_path)

        init_template(test_project_path / "template_config.yaml", "target_string", dry_run=False)



if __name__ == "__main__":
    unittest.main()
