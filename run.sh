PYTHON_CMD=python
VENV_NAME=ordering
if [! -f "/path/to/file" ]; then
  echo "venv not found, creating venv"
  $PYTHON_CMD -m venv $VENV_NAME
  $PYTHON_CMD -m pip install -r requirements.txt
fi
source $VENV_NAME/bin/activate
$PYTHON_CMD main.py | tee "logs/$(date +"%Y_%m_%d_%A_%I_%M_%p")_ordering.log"
deactivate
