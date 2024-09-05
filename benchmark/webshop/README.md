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