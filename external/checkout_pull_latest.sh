#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

checkout_and_pull () {
  echo "Updating: $1"
  cd $SCRIPT_DIR/$1
  git checkout $2
  git pull origin $2
}

checkout_and_pull template_project_cpp_master/ master
checkout_and_pull template_project_cpp_usecase_qt_qml_app/ usecase/qt_qml_app

checkout_and_pull template_project_kicad_master/ master

checkout_and_pull template_project_python_master/ master
checkout_and_pull template_project_python_usecase_qt_qml_app/ usecase/qt_qml_app
