import ast
import pandas as pd


N_TRIALS = 40

df_trials = pd.read_csv("data.csv")

data = []

for i, row in df_trials.iterrows():

    for trial in range(1, N_TRIALS + 1):

        item = ast.literal_eval(row[f"trial{trial}"])
        item_ratings = item["likertResponses"]
        ratings = [int(item_ratings[key]) for key in sorted(item_ratings.keys())]
        
        if 'cc' in item['structure']:
            causal_structure = 1

        if 'coc' in item['structure']:
            causal_structure = 0
            
        type_ = item['type']
        strength = item['strength']

        data.append({
            "worker_id": row["workerid"],
            "scenario_id": item["scenario_id"],
            "rating": ratings[0],
            "structure": causal_structure,
            "type": type_,
            "strength": strength,
            
            
        })

df_long = pd.DataFrame(data)

df_long.to_csv("data_combined_long.csv", index=False)