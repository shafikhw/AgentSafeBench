import json
from typing import List, Dict
from pathlib import Path
from benchmark.schema import Scenario

def load_scenarios(file_path: str) -> List[Scenario]:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    scenarios = []
    for item in data:
        scenario = Scenario(**item)
        scenarios.append(scenario)
    return scenarios
    
def load_all_scenarios(directory: str) -> List[Scenario]:
    scenarios = []
    p = Path(directory)
    if not p.exists():
        return scenarios
        
    for json_file in p.glob('scenarios_*.json'):
        scenarios.extend(load_scenarios(str(json_file)))
        
    return scenarios
