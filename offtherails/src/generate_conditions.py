import os
import csv

DATA_DIR = '../data'
CONDITION_DIR =  '../data/conditions_mild_harm_mild_good'


EVITABILITY = ['evitable', 'inevitable']
ACTION = ['action_yes', 'prevention_no']


def get_completions(csv_name="coc_stage_2_mild.csv"):
    with open(f"{DATA_DIR}/{csv_name}", newline='') as f:
        reader = csv.reader(f, delimiter=";")
        completions = list(reader)
    print(completions)
    return completions

def generate_conditions(completions, csv_name="coc_stage_2_mild.csv", structure="cc"):
    list_var = ["Context", 
                "Action Opportunity", 
                "Harm", 
                "Good", 
                "Preventable Cause", 
                "Non-Preventable Cause",
                "Structure", 
                "Evitable Action", 
                "Inevitable Action",
                "Evitable Prevention", 
                "Inevitable Prevention", 
                "Action", 
                "Prevention"]
                
    for completion_idx, completion in enumerate(completions):

        dict_var = {k:v for k,v in zip(list_var, completion)}

        context = dict_var['Context'] # context (constant)
        name = context.split(',')[0]
        belief_question = "The agent "
        intention_question = ""
        belief_question = belief_question.format(name=name)
        intention_question = intention_question.format(name=name)

        for evitability in EVITABILITY:

            for action in ACTION:

                if evitability == 'evitable':

                    if action == 'action_yes':
                        action_var = dict_var['Action Opportunity']
                        evitable_action = dict_var["Evitable Action"]
                        action_sentence = dict_var["Action"]
                    
                    
                    if action == 'prevention_no':
                        action_var = dict_var["Preventable Cause"]
                        evitable_action = dict_var["Evitable Prevention"]
                        action_sentence = dict_var["Prevention"]
        
                if evitability == 'inevitable':
                        
                        if action == 'action_yes':
                            action_var = dict_var["Action Opportunity"]
                            evitable_action = dict_var["Inevitable Action"]
                            action_sentence = dict_var["Action"]
                        
                        
                        if action == 'prevention_no':
                            action_var = dict_var["Preventable Cause"]
                            evitable_action = dict_var["Inevitable Prevention"]
                            action_sentence = dict_var["Prevention"]

                # Check if the new file needs to be created or appended
                if not os.path.exists(os.path.join(CONDITION_DIR)):
                    os.makedirs(os.path.join(CONDITION_DIR))
                new_csv_file = os.path.join(CONDITION_DIR, f'{structure}_{evitability}_{action}_stories.csv')
                with open(new_csv_file, "a" if completion_idx > 0 else "w", newline='') as csvfile:
                    writer = csv.writer(csvfile, delimiter=";")
                    if structure == "cc":
                        writer.writerow([context, action_var, dict_var["Structure"], evitable_action, action_sentence])
                    elif structure == "coc":    
                        writer.writerow([context, action_var, dict_var["Harm"], dict_var["Structure"], evitable_action, action_sentence]) # harm and good are flipped here 


if __name__ == "__main__":  
    completions = get_completions(csv_name="coc_stage_2_mild.csv")
    generate_conditions(completions, csv_name="coc_stage_2_mild.csv", structure="coc")

