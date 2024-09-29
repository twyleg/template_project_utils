# Copyright (C) 2024 twyleg
import versioneer
from pathlib import Path
from setuptools import find_packages, setup


def read(relative_filepath):
    return open(Path(__file__).parent / relative_filepath).read()


def read_long_description() -> str:
    return read("README.md")


# fmt: off
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
    install_requires=[
        "simple-python-app==0.3.0",
        "pygit2~=1.15.1",
        "inquirerpy~=0.3.4",
    ],
    entry_points={
        "console_scripts": [
            "template_project_utils = template_project_utils.main:main",
        ]
    },
)
