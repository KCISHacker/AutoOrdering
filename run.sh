if [! -f "/path/to/file" ]; then
  echo "venv not found, creating venv"
  python3 -m venv order
  python3 -m pip install -r requirements.txt
fi
source order/bin/activate
python main.py | tee "logs/$(date +"%Y_%m_%d_%A_%I_%M_%p")_ordering.log"
deactivate
