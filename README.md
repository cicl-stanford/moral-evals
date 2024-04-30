##  
Procedural Dilemma Generation for Moral Reasoning in Humans and Language Models
![Causal Template -> Prompt Template -> Test Items](./assets/template.png)

### 🧐 What is this?
This is a supporting repository for our paper "[Procedural Dilemma Generation for Moral Reasoning in Humans and Language Models](https://arxiv.org/abs/2404.10975)" (2024, _CogSci_).

- [Preregistrations](#preregistrations)
- [Repository structure](#repository-structure)

#### Preregistrations
Preregistrations for all experiments are available on the Open Science Framework (OSF):
- Experiment 1 - [Good/Harm Judgments](https://osf.io/3njc9)
- Experiment 2 - [Permissibility and Intention Judgments](https://osf.io/qupxy)

#### Repository structure

```
├── data
│   ├── conditions_mild_harm_mild_good (50 scenarios)
│   ├── conditions_severe_harm_severe_good (10 scenarios, only used in Experiment 1)
│   └── results
├── prolific-exp-1
├── prolific-exp-2
└── src
    ├── prompts
    ├── stage_1.py
    └── stage_2.py
```

- `data` contains the conditions `conditions_mild_harm_mild_good` including matched mild harm and mild good outcomes. We used to first 10 scenarios from each condition for our comparison in the paper (80 items). We also include `conditions_severe_harm_severe_good` which includes conditions with matched severe harm and severe good outcomes. 
    - `results` include model responses including chain-of-thought examples 
- `prolific-exp-1` and  `prolific-exp-2` include the experimental stimuli and formatted participant data frames (`_long_format.csv`)
- `src` includes prompts and code (`stage_1.py` and  `stage_2.py`) for generating items.
- `docs` contains all the experiment code. You can preview the experiments below:
    - Experiment 1 - [Good/Harm Judgments](https://cicl-stanford.github.io/moral-evals/off-the-rails-1/)
    - Experiment 2 - [Permissibility and Intention Judgments](https://cicl-stanford.github.io/moral-evals/off-the-rails-2/)

