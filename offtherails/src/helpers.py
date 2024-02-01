from typing import List

import csv


def get_vars_from_out(out:str) -> List[str]:
    vars = []
    out = out.split('\n')
    out = [l for l in out if ':' in l]
    for line in out:
        elems = line.split(': ')
        if elems[0] != 'Context':
            vars.append(elems[1].strip())
    return vars


def get_context(name: str, profession: str) -> str:
    if profession.strip()[0].lower() in ['a', 'e', 'i', 'o', 'u']:
        profession = f'an {profession.strip()}'
    else:
        profession = f'a {profession.strip()}'
    context = f"{name.strip()}, {profession}, faces a moral dilemma."
    return context


def get_example(condition: str, rand_item: str, data_dir: str, n_vars: int = 50) -> str:

    vars = {k: None for k in range(n_vars)}

    if condition == "cc":
        with open(f'{data_dir}/cc_stage_2_mild.csv', 'r') as f:
            reader = csv.reader(f, delimiter=';')
            for i, row in enumerate(reader):
                if i == rand_item:
                    for j, elem in enumerate(row):
                        vars[j] = elem.strip()
                    break
        return f"""Context: {vars[0]}
Action Opportunity: {vars[1]}
Harm CC: {vars[2]}
Good CC: {vars[3]}
Preventable Cause CC: {vars[4]}
Non-Preventable Cause CC: {vars[5]}
"As a means to" CC: {vars[6]}
Evitable Action CC: {vars[7]}
Inevitable Action CC: {vars[8]}
Evitable Prevention CC: {vars[9]}
Inevitable Prevention CC: {vars[10]}
Action CC: {vars[11]}
Prevention CC: {vars[12]}"""

    elif condition == "coc":
        with open(f'{data_dir}/coc_stage_2_mild.csv', 'r') as f:  
            reader = csv.reader(f, delimiter=';')
            for i, row in enumerate(reader):
                if i == rand_item:
                    for j, elem in enumerate(row):
                        vars[j] = elem.strip()
                    break
        return f"""Context: {vars[0]}
Action Opportunity: {vars[1]}
Harm CoC: {vars[2]}
Good CoC: {vars[3]}
Preventable Cause CoC: {vars[4]}
Non-Preventable Cause CoC: {vars[5]}
"As a side effect" CoC: {vars[6]}
Evitable Action CoC: {vars[7]}
Inevitable Action CoC: {vars[8]}
Evitable Prevention CoC: {vars[9]}
Inevitable Prevention CoC: {vars[10]}
Action CoC: {vars[11]}
Prevention CoC: {vars[12]}"""