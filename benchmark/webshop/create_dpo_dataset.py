
import json
from datasets import Dataset
# Load the data


def load_data(file_path):
    all_data = {}
    with open(file_path) as f:
        for line in f.readlines():
            
            data = json.loads(line)
            all_data[data["id"]] = data
    return all_data

data0 = load_data("gen_results/Salesforce/xLAM-v0.1-r/HuggingFaceH4/Webshop-AgentQ-dedup/planreact_results_webshop_planreact_all_t1.2_00.csv")
data1 = load_data("gen_results/Salesforce/xLAM-v0.1-r/HuggingFaceH4/Webshop-AgentQ-dedup/planreact_results_webshop_planreact_all_t1.2_01.csv")



dataset = []

# some tasks may be missing in one of the files
ids = set(data0.keys()) & set(data1.keys())

for index in ids:
    d0 = data0[index]
    d1 = data1[index]
    
    
    if d0["task"] != d1["task"]:
        print("Error")
        break

    if d0["reward"] > d1["reward"]:
        chosen = d0
        rejected = d1
    else:
        chosen = d1
        rejected = d0
    
    prompt = chosen["message_str"].split(d0["task"]+"\nAction:")[0] + d0["task"]+"\nAction:"
    chosen_messages = [
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": chosen["message_str"].split(d0["task"]+"\nAction:")[1]},
    ]
    rejected_messages = [
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": rejected["message_str"].split(d0["task"]+"\nAction:")[1]},
    ]
    
    
    example = {
        "prompt": prompt,
        "chosen": chosen_messages,
        "rejected": rejected_messages,
        "messages": chosen_messages,
        "score_chosen": chosen["reward"],
        "score_rejected": rejected["reward"],
    }
    
    dataset.append(example)

dataset = Dataset.from_list(dataset)
dataset = dataset.train_test_split(test_size=100, seed=42)

dataset.push_to_hub("HuggingFaceH4/Webshop-xLAM-v0.1-r-PLANREACT-DPO-all-t1.2", private=True)

def margin_filter(example):
    return abs(example["score_chosen"] - example["score_rejected"]) > 0.0

dataset = dataset.filter(margin_filter)
dataset.push_to_hub("HuggingFaceH4/Webshop-xLAM-v0.1-r-PLANREACT-DPO-all-t1.2-margin-filtered", private=True)