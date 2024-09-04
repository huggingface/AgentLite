# Instructions to run on the Hugging Face Cluster

## Run on an interactive node

In an interactive node, run:

```shell
./launch_webshop.slurm Salesforce/xLAM-v0.1-r
```

## Launch a Slurm job

To launch a job, run:

```shell
sbatch --job-name=webshop launch_webshop.slurm Salesforce/xLAM-v0.1-r
```