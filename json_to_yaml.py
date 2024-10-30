import json
import yaml

with open("config.json", "r") as f:
    data = json.load(f)

with open("config.yaml", "w") as f:
    yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

