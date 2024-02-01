from collections import defaultdict
import json
import os
import numpy as np

# Constants
DATA_DIR = '../'
NUM_CONDITIONS = 8
START_SCENARIOS = 5
END_SCENARIOS = 10
NUM_BATCHES = 1



# Function to read CSV
def read_csv(csv_file):
    with open(csv_file, 'r') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        lines[i] = line.strip().split(';')
    return [l[:3] for l in lines]

# Define all conditions
causal_structure = ['cc', 'coc']

test_items = []

# Read all the data
for cs in causal_structure:
    csv_path_severe = os.path.join(DATA_DIR, f"{cs}_stage_1_severe.csv")
    csv_path_mild = os.path.join(DATA_DIR, f"{cs}_stage_1_mild.csv")
    try:
        csv_data_severe = read_csv(csv_path_severe)
        csv_data_mild = read_csv(csv_path_mild)
    except FileNotFoundError:
        print(f"File {csv_path_severe} and/or {csv_path_mild} not found.")
        continue
    for s, story in enumerate(csv_data_severe[START_SCENARIOS:END_SCENARIOS]):
        if cs == 'cc':
            test_items.append({"background": story[0], "target": story[1], "scenario_id": s + START_SCENARIOS, "structure": cs, "type": "harm", "strength": "severe"})
            test_items.append({"background": story[0], "target": story[2], "scenario_id": s + START_SCENARIOS, "structure": cs, "type": "good", "strength": "severe"})
        elif cs == 'coc':
            test_items.append({"background": story[0], "target": story[2], "scenario_id": s + START_SCENARIOS, "structure": cs, "type": "harm", "strength": "severe"})
            test_items.append({"background": story[0], "target": story[1], "scenario_id": s + START_SCENARIOS, "structure": cs, "type": "good", "strength": "severe"})

    for s, story in enumerate(csv_data_mild[START_SCENARIOS:END_SCENARIOS]):
        if cs == 'cc':
            test_items.append({"background": story[0], "target": story[1], "scenario_id": s + START_SCENARIOS, "structure": cs, "type": "harm", "strength": "mild"})
            test_items.append({"background": story[0], "target": story[2], "scenario_id": s + START_SCENARIOS, "structure": cs, "type": "good", "strength": "mild"})
        elif cs == 'coc':
            test_items.append({"background": story[0], "target": story[2], "scenario_id": s + START_SCENARIOS, "structure": cs, "type": "harm", "strength": "mild"})
            test_items.append({"background": story[0], "target": story[1], "scenario_id": s + START_SCENARIOS, "structure": cs, "type": "good", "strength": "mild"})

# with open(f'batch_1.json', 'w') as f:
#     json.dump(test_items, f)