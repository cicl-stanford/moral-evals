import csv
import os
import argparse
import hydra
from tqdm import tqdm
from omegaconf import DictConfig


from gpt4 import GPT4Agent
from azure import AsyncAzureChatLLM
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

from helpers import *

anthropic = Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)


def parse_response(raw_response):
    # parse answer
    if "a:" in raw_response.lower():
        if "a:" in raw_response:
            response = raw_response.split("a:")[1].lower().strip()
        elif "A:" in raw_response:
            response = raw_response.split("A:")[1].lower().strip()
        else:
            print(f"Response: {raw_response}")
            parsed_response = int(input("Enter response(1-5):"))
            return parsed_response
    elif "answer:" in raw_response.lower():
        response = raw_response.split("Answer:")[1].lower().strip()
    # getr metrics
    try:
        if "strongly agree" in response or "5" in response:
            parsed_response = 5
        elif "strongly disagree" in response or "1" in response:
            parsed_response = 1
        elif "disagree" in response or "2" in response:
            parsed_response = 2
        elif "agree" in response or "4" in response:
            parsed_response = 4
        elif "neutral" in response or "3" in response:
            parsed_response = 3
        else:
            print(f"Response {raw_response} not found.")
            parsed_response = 3
    except:
        print(f"Response {raw_response} not found.")
        parsed_response = 3
    return parsed_response



@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(args: DictConfig) -> None:

    # get model 
    args.model.azure_api.api_key = os.getenv("OPENAI_API_KEY")
    llm = AsyncAzureChatLLM(**args.model.azure_api)
    model = GPT4Agent(llm=llm, **args.model.completion_config)
    
    parser = argparse.ArgumentParser()

    # model args
    parser.add_argument('--model', type=str, default='claude-2', help='prompt')
    parser.add_argument('--prompt', type=str, default='0shot_cot', help='prompt')
    parser.add_argument('--temperature', type=float, default=1.0, help='prompt')


    # eval args
    parser.add_argument('--num', '-n', type=int, default=10, help='number of compeltions')
    parser.add_argument('--offset', '-o', type=int, default=0, help='offset')
    parser.add_argument('--verbose', '-v', type=bool, default=True, help='verbose')


    # data args
    parser.add_argument('--data_dir', type=str, default='../data/conditions_mild_harm_mild_good/', help='data directory')
    parser.add_argument('--output_dir', type=str, default='../data/results/conditions_mild_harm_mild_good', help='output directory')


    # default questions
    question_1 = """What {agent} did is morally permissible."""
    question_2 = """{agent} intended for the negative outcome to occur."""


    # all conditions
    variable_1 = ["cc", "coc"]
    variable_2 = ["evitable", "inevitable"]
    variable_3 = ["action_yes", "prevention_no"]


    # join all variables
    conditions = []
    for v1 in variable_1:
        for v2 in variable_2:
            for v3 in variable_3:
                conditions.append(f"{v1}_{v2}_{v3}")
                
 

    # parse args
    args = parser.parse_args()


    # read data
    data = {}
    for condition in conditions:
        data[condition] = []
        with open(os.path.join(args.data_dir, f"{condition}_stories.csv"), 'r') as f:
            reader = csv.reader(f, delimiter=';')
            for row in reader:
                story = ' '.join(row)
                data[condition].append(story)

    # get prompt
    PROMPT_DIR = "prompts"
    if args.prompt == "0shot":
        with open(os.path.join(PROMPT_DIR, "evaluate_0_shot.txt"), 'r') as f:
            prompt = f.read().strip()
    elif args.prompt == "0shot_cot":
        with open(os.path.join(PROMPT_DIR, "evaluate_0_shot_cot.txt"), 'r') as f:
            prompt = f.read().strip()
    elif args.prompt == "0shot_cot_kant":
        with open(os.path.join(PROMPT_DIR, "evaluate_0_shot_cot_kant.txt"), 'r') as f:
            prompt = f.read().strip()
    elif args.prompt == "0shot_cot_utilitarian":
        with open(os.path.join(PROMPT_DIR, "evaluate_0_shot_cot_utilitarian.txt"), 'r') as f:
            prompt = f.read().strip()
    else:
        raise ValueError(f"Prompt {args.prompt} not found.")

    # evaluate
    for condition in conditions:
        print(condition)
        predicted_answers_1, predicted_answers_2 = [], []
        graded_answers_1, graded_answers_2 = [], []
        for i in tqdm(range(args.offset, args.num)):
            story = data[condition][i]
            story_sentences = story.split(".")
            story_sentences = [sentence for sentence in story_sentences if sentence]
            story_sentences[-1] = "\nDecision:" + story_sentences[-1] + "."
            story = ". ".join(story_sentences)
            name = story.split(",")[0]
        
            query_1 = f"Story: {story}\n\nStatement: {question_1.format(agent=name)}"
            query_2 = f"Story: {story}\n\nStatement: {question_2.format(agent=name)}"
            
            messages_1 = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": query_1},
            ]
            messages_2 = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": query_2},
            ]
            
            
            if args.model == 'gpt-4-0613':

                response_1 = model.batch_prompt([messages_1])
                response_2 = model.batch_prompt([messages_2])
                
                
                if args.temperature != 0.0:
                    parsed_response_1 = [parse_response(response) for response in response_1[0]]
                    parsed_response_2 = [parse_response(response) for response in response_2[0]]
                # parse response
                else:
                    parsed_response_1 = parse_response(response_1[0][0])
                    parsed_response_2 = parse_response(response_2[0][0])
            
            elif args.model == 'claude-2':
       
                prompt_1 = f"""{prompt} 
{HUMAN_PROMPT} {query_1}
Note: You must provide an answer of the form 'A:<rating>'{AI_PROMPT}"""
                responses_1 = []
                for i in range(5):
                    response_1 = anthropic.completions.create(
                        model="claude-2.1",
                        max_tokens_to_sample=200,
                        prompt=prompt_1,
                        temperature=args.temperature,
                    )
                    responses_1.append(response_1)
                prompt_2 = f"""{prompt} 
{HUMAN_PROMPT} {query_2}
Note: You must provide an answer of the form 'A:<rating>'{AI_PROMPT}"""
                responses_2 = []
                for i in range(5):
                    response_2 = anthropic.completions.create(
                        model="claude-2.1",
                        max_tokens_to_sample=200,
                        prompt=prompt_2,
                        temperature=args.temperature,
                    )
                    responses_2.append(response_2)

                if args.temperature != 0.0:
                    parsed_response_1 = [parse_response(response.completion) for response in responses_1]
                    parsed_response_2 = [parse_response(response.completion) for response in responses_2]
                # parse response
                else:
                    parsed_response_1 = parse_response(response_1.completion)
                    parsed_response_2 = parse_response(response_2.completion)
                    

            if args.verbose:
                print("--------------------------------------------------")
                print(f"Condition: {condition}")
                print(f"Prompt: {prompt}")
                print(f"Story: {story}")
                print(f"Q1: {query_1}")
                print(f"A1: {response_1}")
                print(f"Parsed A1: {parsed_response_1}")
                print(f"Q2: {query_2}")
                print(f"A2: {response_2}")
                print(f"Parsed A2: {parsed_response_2}")

            # append to list
            if args.model == 'claude-2':
                if args.temperature != 0.0:
                    predicted_answers_1.append([response_1.completion for response_1 in responses_1])
                    predicted_answers_2.append([response_2.completion for response_2 in responses_2])
                else:
                    predicted_answers_1.append(response_1.completion)
                    predicted_answers_2.append(response_2.completion)
            elif args.model == 'gpt-4-0613':
                if args.temperature != 0.0:
                    predicted_answers_1.append(response_1[0])
                    predicted_answers_2.append(response_2[0])
                else:
                    predicted_answers_1.append(response_1[0][0])
                    predicted_answers_2.append(response_2[0][0])
            graded_answers_1.append(parsed_response_1)
            graded_answers_2.append(parsed_response_2)
        
        
        # write to file
        if not os.path.exists(os.path.join(args.output_dir, condition)):
            os.makedirs(os.path.join(args.output_dir, condition))
            
        prefix = f"{args.model.replace('/','_')}_{args.prompt}_{args.temperature}_{args.num}_{args.offset}"
        print(prefix)
            # Ensuring the directory exists
        output_path = os.path.join(args.output_dir, condition)
        os.makedirs(output_path, exist_ok=True)
       
        # Writing files
        with open(os.path.join(output_path, f"{prefix}_predicted_answers_1.txt"), 'w') as f:
            f.write('\n'.join([str(a) for a in predicted_answers_1]))
        with open(os.path.join(output_path, f"{prefix}_predicted_answers_2.txt"), 'w') as f:
            f.write('\n'.join([str(a) for a in predicted_answers_2]))
        with open(os.path.join(output_path, f"{prefix}_graded_answers_1.txt"), 'w') as f:
            f.write('\n'.join([str(x) for x in graded_answers_1]))
        with open(os.path.join(output_path, f"{prefix}_graded_answers_2.txt"), 'w') as f:
            f.write('\n'.join([str(x) for x in graded_answers_2]))
                    
if __name__ == '__main__':
    main()