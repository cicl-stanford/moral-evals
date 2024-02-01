from collections import defaultdict
import json
import os
import numpy as np

# Constants
DATA_DIR = '../data/conditions_mild_harm_mild_good'
NUM_CONDITIONS = 8
NUM_SCENARIOS = 10
NUM_BATCHES = 5
PER_BATCH = NUM_CONDITIONS * NUM_SCENARIOS // NUM_BATCHES

np.random.seed(0)

# Function to read CSV
def read_csv(csv_file):
    with open(csv_file, 'r') as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        lines[i] = line.strip().split(';')
    return lines

# Define all conditions
causal_structure = ['cc', 'coc']
evitability = ['evitable', 'inevitable']
action = ['action_yes', 'prevention_no']


# Read all the data
data = [[] for _ in range(NUM_SCENARIOS)]
for cs in causal_structure:
    for ev in evitability:
        for act in action:
            condition_name = f"{cs}_{ev}_{act}"
            csv_path = os.path.join(DATA_DIR, f"{condition_name}_stories.csv")
            try:
                csv_data = read_csv(csv_path)
            except FileNotFoundError:
                print(f"File {csv_path} not found.")
                continue
            
            for s, story in enumerate(csv_data[:NUM_SCENARIOS]):
                data[s].append([story, condition_name])

print(f"Total number of scenarios: {len(data)}")
for s in range(NUM_SCENARIOS):
    print(f"Scenario {s}: {len(data[s])} conditions")

# Initialize batches
batches = [[] for _ in range(NUM_BATCHES)]
num_sampled_scenario = [0 for _ in range(NUM_SCENARIOS)]
rand_ids = [[] for _ in range(NUM_BATCHES)]
unsampled_ids = [[0 for _ in range(NUM_CONDITIONS)] for _ in range(NUM_SCENARIOS)]

for b in range(NUM_BATCHES):
    # sample stories such that each batch has at most 2 conditions per scenario
    num_sampled = [0 for _ in range(NUM_SCENARIOS)]
    while len(batches[b]) < PER_BATCH:
        # print logs
        print(f"Batch {b}: {len(batches[b])}/{PER_BATCH}, {num_sampled.count(2)}/{NUM_SCENARIOS} scenarios sampled twice")
        print(f"Number of scenarios sampled: {num_sampled_scenario}")
        print(rand_ids[b])

        # get list of scenarios that have not been sampled twice
        if len(batches[b]) < NUM_SCENARIOS:
            try:
                unsampled_scenarios = [i for i in range(NUM_SCENARIOS) if num_sampled[i] == 0 and unsampled_ids[i].count(0) > 0]
                # sample a random scenario
                random_idx = np.random.choice(unsampled_scenarios)
            except:
                unsampled_scenarios = [i for i in range(NUM_SCENARIOS) if num_sampled[i] < 3 and unsampled_ids[i].count(0) > 0]
                # sample a random scenario
                random_idx = np.random.choice(unsampled_scenarios)
    
        else:
            try:
                unsampled_scenarios = [i for i in range(NUM_SCENARIOS) if num_sampled[i] == 1 and unsampled_ids[i].count(0) > 0]
                # sample a random scenario
                random_idx = np.random.choice(unsampled_scenarios)
            except:
                unsampled_scenarios = [i for i in range(NUM_SCENARIOS) if num_sampled[i] < 3 and unsampled_ids[i].count(0) > 0]
                # sample a random scenario
                random_idx = np.random.choice(unsampled_scenarios)
    


        # sample a random scenario
        random_idx = np.random.choice(unsampled_scenarios)
        # get list of conditions that have not been sampled
        unsampled_conditions = [i for i in range(NUM_CONDITIONS) if unsampled_ids[random_idx][i] == 0]

        print(f"Unsampled Conditions: {unsampled_conditions}")
        # sample a random condition
        random_condition = np.random.choice(unsampled_conditions)
        # sample the condition
        unsampled_ids[random_idx][random_condition] = 1
        num_sampled[random_idx] += 1
        num_sampled_scenario[random_idx] += 1
        # add the story to the batch
        rand_ids[b].append(random_idx)
        s = random_idx
        condition = random_condition
        condition_name = data[s][condition][1]
       
        try:
            context, opportunity, structure_sentence, evitability_sentence, action_sentence = data[s][condition][0] 
        except:
            context, opportunity, structure_sentence_1, structure_sentence_2, evitability_sentence, action_sentence = data[s][condition][0] 
            structure_sentence = structure_sentence_1 + " " + structure_sentence_2
        agent = context.split(',')[0]
        story = {
            'permissibility_question': f"What {agent} did is morally permissible.",
            'intention_question': f"{agent} intended for the negative outcome to occur.",
            'context': context,
            'opportunity': opportunity,
            'structure_sentence': structure_sentence,
            'evitability_sentence': evitability_sentence,
            'action_sentence': action_sentence,
            'scenario_id': int(random_idx),
            'condition': condition_name,
        }
        batches[b].append(story)
    

# Write the batches to JSON files
for i, batch in enumerate(batches):
    with open(f'batch_{i}.json', 'w') as f:
        json.dump(batch, f)
