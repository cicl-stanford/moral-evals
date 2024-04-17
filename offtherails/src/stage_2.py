import os
import logging

import random
import hydra
from itertools import islice
from tqdm import tqdm
import pandas as pd
from omegaconf import DictConfig


from gpt4 import GPT4Agent
from azure import AsyncAzureChatLLM

from helpers import *


logging.basicConfig(level=logging.INFO)

@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(args: DictConfig) -> None:

    # get model 
    args.model.azure_api.api_key = os.getenv("OPENAI_API_KEY")
    llm = AsyncAzureChatLLM(**args.model.azure_api)
    model = GPT4Agent(llm=llm, **args.model.completion_config)

    
    # number of total possible names
    vars = {k: None for k in range(args.data.n_vars)}

    # load names 
    with(open(f'{args.prompts.prompt_dir}/names.txt', 'r')) as f:
        names = f.readlines()

    # load professions
    with(open(f'{args.prompts.prompt_dir}/professions.txt', 'r')) as f: 
        professions = f.readlines()

    # main loop
    for i in range(args.data.start, args.data.end):
        
        # name and profession
        name = names[i]
        profession = professions[i]

        # load example for few shot prompt
        rand_item = args.data.single_shot if not args.data.random_single_shot else random.randint(0, args.data.start)
        example = get_example(condition=args.data.condition, 
                              rand_item=rand_item,
                              data_dir=args.data.data_dir,
                              n_vars=args.data.n_vars,
        )
    
        # concat messages
        messages = []
        if args.data.condition == "cc":
            with(open(f'{args.prompts.prompt_dir}/cc_stage_2.txt', 'r')) as f:
                system_prompt = f.read().strip()
            
            with(open(f'{args.data.data_dir}/cc_stage_1_{args.data.severity}.csv', 'r')) as f:
                reader = csv.reader(f, delimiter=';')
                new_item = list(reader)[i]
     
            human_message_1 = f"""Generate a new completion for this context: 
Context: {get_context(name=name, profession=profession)}
Action Opportunity: {new_item[0]}
Harm CC: {new_item[1]}
Good CC: {new_item[2]}
Preventable Cause CC: {new_item[3]}
Non-Preventable Cause CC: {new_item[4]}"""

        elif args.data.condition == "coc":
            with(open(f'{args.prompts.prompt_dir}/coc_stage_2.txt', 'r')) as f:
                system_prompt = f.read().strip()

            with(open(f'{args.data.data_dir}/coc_stage_1_{args.data.severity}.csv', 'r')) as f:
                reader = csv.reader(f, delimiter=';')
                new_item = list(reader)[i]

            human_message_1 = f"""Generate a new completion for this context: 
Context: {get_context(name=name, profession=profession)}
Action Opportunity: {new_item[0]}
Good CoC: {new_item[1]}
Harm CoC: {new_item[2]}
Preventable Cause CoC: {new_item[3]}
Non-Preventable Cause CoC: {new_item[4]}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Generate a completion."},
            {"role": "assistant", "content": example},
            {"role": "user", "content": human_message_1},
        ]
        
        responses = model.batch_prompt(batch_messages=[messages])
        responses = responses[0] # since we are not batching atm

        for response in responses:
            if args.data.verbose:
                print(f"------ Human Message ------")
                print(human_message_1)
                print(f"------ Generated Story ------")
                print(response)
                print("------------ Fin --------------")

            new_vars = get_vars_from_out(response)
            
            vars = [get_context(name=name, profession=profession)] + new_item + new_vars
    
            if args.data.condition == "cc":
                with open(f'{args.data.data_dir}/cc_stage_2_{args.data.severity}.csv', 'a') as csvfile:
                    writer = csv.writer(csvfile, delimiter=';')
                    writer.writerow(vars)
            elif args.data.condition == "coc":
                with open(f'{args.data.data_dir}/coc_stage_2_{args.data.severity}.csv', 'a') as csvfile:
                    writer = csv.writer(csvfile, delimiter=';')
                    writer.writerow(vars)
    
if __name__ == '__main__':
    main()