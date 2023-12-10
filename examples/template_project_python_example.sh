#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

mkdir -p $SCRIPT_DIR/data/
rm -f -r $SCRIPT_DIR/data/*

cp -r $SCRIPT_DIR/../external/template_project_python/ $SCRIPT_DIR/data/example_project_python

export PYTHONPATH=$PYTHONPATH:$SCRIPT_DIR/..

cd $SCRIPT_DIR/data/example_project_python
python -m template_project_utils example_project_python
