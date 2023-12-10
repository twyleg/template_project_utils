#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

mkdir -p $SCRIPT_DIR/data/
rm -f -r $SCRIPT_DIR/data/*

python -m venv venv
source venv/bin/activate

pip install $SCRIPT_DIR/..

cp -r $SCRIPT_DIR/../external/template_project_python/ $SCRIPT_DIR/data/example_project_python
cp -r $SCRIPT_DIR/../external/template_project_kicad/ $SCRIPT_DIR/data/example_project_kicad


cd $SCRIPT_DIR/data/example_project_python
template_project_utils -vv example_project_python

cd $SCRIPT_DIR/data/example_project_kicad
template_project_utils -vv example_project_kicad
