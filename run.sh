#! /usr/bin/env bash
PYTHON_CMD=python
VENV_NAME=ordering
if [ ! -d $VENV_NAME ]; then
  echo "venv not found, creating venv"
  $PYTHON_CMD -m venv $VENV_NAME
  source $VENV_NAME/bin/activate
  $PYTHON_CMD -m pip install -r requirements.txt
else
  source $VENV_NAME/bin/activate
fi
if [ ! -d "logs" ]; then
  mkdir logs
fi
$PYTHON_CMD main.py | tee "logs/$(date +"%Y_%m_%d_%A_%I_%M_%p")_ordering.log"
deactivate
