import ast
import pandas as pd


N_TRIALS = 16

df_trials = pd.read_csv("trials.csv")
df_ids = pd.read_csv("pid.csv")
df_exit = pd.read_csv("exit.csv")

data = []


for i, row in df_trials.iterrows():

    prolific_id = df_ids.iloc[i]["prolificPid"]
    exit_survey = df_exit.iloc[i]
    age = exit_survey["age"]
    ethnicity = exit_survey["ethnicity"]
    gender = exit_survey["gender"]
    race = exit_survey["race"]
    
    for trial in range(1, N_TRIALS + 1):

        item = ast.literal_eval(row[f"trial{trial}"])
        item_ratings = item["likertResponses"]
        ratings = [int(item_ratings[key]) for key in sorted(item_ratings.keys())]

        condition = item["condition"]

        if 'cc_' in condition:
            causal_structure = 1

        if 'coc_' in condition:
            causal_structure = 0

        if 'evitable' in condition and 'inevitable' not in condition:
            evitability = 1

        if 'inevitable' in condition:
            evitability = 0

        if 'action_yes' in condition:
            action = 1

        if 'prevention_no' in condition:
            action = 0
      
        data.append({
            "split": row["proliferate.condition"],
            "worker_id": row["workerid"],
            "scenario_id": item["scenario_id"],
            "scenario_harm": 0,
            "permissibility_rating": ratings[0],
            "intention_rating": ratings[1],
            "causal_structure": causal_structure,
            "evitability": evitability,
            "action": action,
        })

df_long = pd.DataFrame(data)


df_long.to_csv("data_long.csv", index=False)