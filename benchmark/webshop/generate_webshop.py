from typing import List
from tqdm.auto import tqdm
import os
import argparse
import pandas as pd
import json


from datasets import load_dataset

from webshop_agents import WebshopAgent
from webshop_env import Webshop
from webshop_multiagent import bolaa_webagent

from agentlite.actions import BaseAction, FinishAct, ThinkAct
from agentlite.actions.InnerActions import INNER_ACT_KEY
from agentlite.agents import ABCAgent, BaseAgent
from agentlite.commons import AgentAct, TaskPackage
from agentlite.llm.agent_llms import BaseLLM, get_llm_backend
from agentlite.llm.LLMConfig import LLMConfig
from agentlite.logging.terminal_logger import AgentLogger

# using this function to rerun the evaluation if breaks
def get_runned_ids(file_path):
    try:
        with open(file_path, "r") as file:
            runned_ids = [int(line.split()[0]) for line in file]
        return runned_ids
    except FileNotFoundError:
        print("The file was not found.")
        return None
    except ValueError:
        print("The last item in the last line is not a valid number.")
        return None


GEN_RESULTS_DIR = "gen_results"
# Get full path of the directory and create it if it does not exist
if not os.path.exists(GEN_RESULTS_DIR):
    os.makedirs(GEN_RESULTS_DIR)


webshop_env = Webshop()


def generate(idx: int, llm_name="gpt-3.5-turbo-16k-0613", agent_arch="react", PROMPT_DEBUG_FLAG=False):
    TEMPERATURE = 1.2
    if llm_name in ["xlam", "xlam_v2"]:
        LAM_URL = os.environ["LAM_URL"]
        llm_config = LLMConfig(
            {
                "llm_name": llm_name, 
                "temperature": TEMPERATURE, 
                "base_url": LAM_URL,
                "api_key": "EMPTY"
            }
        )
    else:
        llm_config = LLMConfig({"llm_name": llm_name, "temperature": TEMPERATURE})
    llm = get_llm_backend(llm_config)
    env_idx = f"fixed_{idx}"
    if agent_arch in ["bolaa"]:
        agent = bolaa_webagent(session_idx=env_idx, env=webshop_env, llm=llm, PROMPT_DEBUG_FLAG=PROMPT_DEBUG_FLAG)
        task = agent.goal
        agent.run()
    else:
        # reset the env first if not using bolaa agent
        action = "reset[]"
        webshop_env.step(env_idx, action)
        agent = WebshopAgent(session_idx=env_idx, env=webshop_env, llm=llm, agent_arch=agent_arch, PROMPT_DEBUG_FLAG=PROMPT_DEBUG_FLAG)
        task = webshop_env.goal
        print(f"Task: {task}")
        task_package = TaskPackage(instruction=task)
        agent(task_package)
    reward = webshop_env.reward
    sub_reward = webshop_env.sub_reward
    return reward, sub_reward, task, llm.message_history


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Test Search Agent on the webshop Benchmark"
    )
    parser.add_argument(
        "--llm",
        type=str,
        default="gpt-3.5-turbo-16k-0613",
        help="Name of the language model",
    )
    parser.add_argument(
        "--agent_arch",
        type=str,
        choices=["react", "act", "planact", "planreact", "zs", "zst", "bolaa"],
        default="react",
        help="agent reasoning type",
    )
    parser.add_argument(
        "--debug",
        action='store_true',
        help="debug flag",
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="HuggingFaceH4/Webshop-AgentQ-dedup",
        help="Name of the language model",
    )    
    parser.add_argument(
        "--split",
        type=str,
        default="train",
        help="Name of the language model",
    )    
    parser.add_argument(
        "--num_examples",
        type=int,
        default=-1,
        help="Name of the language model",
    )    
    parser.add_argument(
        "--output_name",
        type=str,
        default="results_webshop",
        help="Name of the language model",
    )    
    

    args = parser.parse_args()
    print(f"loading dataset {args.dataset} {args.split}")
    
    dataset = load_dataset(args.dataset, split=args.split)
    if args.num_examples != -1:
        dataset = dataset.select(range(args.num_examples))   
    
    num_examples = len(dataset)
    all_task_ids = list(range(0, num_examples))

    GEN_RESULTS_DIR = os.path.join(GEN_RESULTS_DIR, args.llm, args.dataset)
    if not os.path.exists(GEN_RESULTS_DIR):
        os.makedirs(GEN_RESULTS_DIR)
    GEN_LOG_FILE = os.path.join(GEN_RESULTS_DIR, f"{args.agent_arch}_{args.output_name}.csv")
    runned_ids = get_runned_ids(GEN_LOG_FILE)
    if runned_ids is None:
        gen_ids = all_task_ids
    else:
        gen_ids = [id for id in all_task_ids if id not in runned_ids]

    # running webshop generation
    with open(GEN_LOG_FILE, "a") as f:
        for i in tqdm(gen_ids):
            try:
                reward, subreward, task, llm_message_history = generate(i, llm_name=args.llm, agent_arch=args.agent_arch, PROMPT_DEBUG_FLAG=args.debug)
                reward_str = f"""{i}\t{task}\t{subreward}\t{reward}\n"""
                
                example = {
                    "id": i,
                    "task": task,
                    "subreward": subreward,
                    "reward": reward,
                    "message_str": llm_message_history[-1][0]['content']
                    
                }
                f.write(json.dumps(example)+"\n")
            except Exception as e:
                print(f"Error in task {i}: {e}")
            
              
    # calculate the average reward
    # read the file and calculate the average reward
    # with open(GEN_LOG_FILE, "r") as f:
    #     lines = f.readlines()
    #     rewards = [float(line.split('\t')[3]) for line in lines]
    
    # avg_reward = sum(rewards) / len(rewards)
    # print(f"The average reward is: {avg_reward}")

    # # Fix up the columns and save the results to a csv file
    # df = pd.read_csv(GEN_LOG_FILE, names=["id", "task", "subreward", "reward"], sep="\t")
    # df.to_csv(GEN_LOG_FILE, index=False)

    
    # with open("complexity.csv") as f:
    #     lines = f.readlines()
    #     complexity = [line.split(',')[1].strip() for line in lines]
    # hard_reward = []
    # easy_reward = []
    # for i, c in enumerate(complexity):
    #     if c == "easy":
    #         easy_reward.append(rewards[i])
    #     elif c == "hard":
    #         hard_reward.append(rewards[i])
    #     else:
    #         raise ValueError("Invalid complexity value")
    # print(f"Average reward for easy tasks: {sum(easy_reward) / len(easy_reward)}")
    # print(f"Average reward for hard tasks: {sum(hard_reward) / len(hard_reward)}")
        
    
    