# Copyright (C) 2023 twyleg
import versioneer
from pathlib import Path
from setuptools import find_packages, setup


def read(relative_filepath):
    return open(Path(__file__).parent / relative_filepath).read()


def read_long_description() -> str:
    return read("README.md")


setup(
    name="template_project_utils",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Torsten Wylegala",
    author_email="mail@twyleg.de",
    description="Utilities to initialize template projects (replacing names, renaming/removing files.",
    license="GPL 3.0",
    keywords="",
    url="https://github.com/twyleg/template_project_utils",
    packages=find_packages(),
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=["pyyaml~=6.0.1", "types-pyyaml~=6.0.12.12", "jsonschema~=4.20.0", "types_jsonschema~=4.20.0.0"],
    entry_points={
        "console_scripts": [
            "template_project_utils = template_project_utils.main:main",
        ]
    },
)
