# Instructions to run on the Hugging Face Cluster

## Run on an interactive node

In an interactive node, run from the root of the repo:

```shell
./benchmark/webshop/launch_webshop.slurm Salesforce/xLAM-v0.1-r
```

## Launch a Slurm job

To launch a job, run from the root of the repo:

```shell
sbatch --job-name=webshop benchmark/webshop/launch_webshop.slurm Salesforce/xLAM-v0.1-r
```

## Lenerating data from the webshop env
Run two jobs and then the benchmark/webshop/create_dpo_dataset.py script (names are hardcoded for now)
```shell
sbatch benchmark/webshop/launch_webshop_gen.slurm Salesforce/xLAM-v0.1-r act "--dataset=HuggingFaceH4/Webshop-AgentQ-dedup --split=train" -1 results_webshop_all_t1.2_001
sbatch benchmark/webshop/launch_webshop_gen.slurm Salesforce/xLAM-v0.1-r act "--dataset=HuggingFaceH4/Webshop-AgentQ-dedup --split=train" -1 results_webshop_all_t1.2_002
```
