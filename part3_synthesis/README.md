# Synthesis: towards a real-world example

Now we combine all the tools and move towards a real-world example:
Simulating and analyzing a full-scale cortical neural network based on
anatomical (structural) data.

In an actual real-world example, many steps of the workflow concern the
data preprocessing. Here we leave this out for simplicity and build upon
an existing model:

```
Schmidt et al. (2018) Multi-scale account of the network structure of macaque visual cortex. Brain Structure and Function 223(3):1409-1435
Schmidt et al. (2018) A multi-scale layer-resolved spiking network model of resting-state dynamics in macaque visual cortical areas. PLOS CB 14(10):e1006359
```

## Tasks

* Understand the workflow
* How does the spiking activity look like?
  * Add a rule and make a script to produce rasterplots of the spiking activity.
* So far, we did not consider any transmission delays, in particular between areas.
  * Add transmission delays to the simulation.

# HPC

* ask Dennis to get a short introduction, to give you access and help you log in using ssh
* activate your project: `jutil env activate -p training1923`
* change to working directory: `cd $PROJECT`
* install conda
* make a new private folder: `mkdir MYNAME && cd MYNAME`
* clone the tutorial repo: `git clone https://github.com/AlexVanMeegen/CNS2019_NEST_Tutorial.git`
* go to repo and install conda environment: `conda env create -f environment.yml`
* run snakemake using SLURM to submit jobs: `snakemake --jobs 10 --cluster-config cluster.json --cluster "sbatch --job-name={cluster.job-name} --account=training1923 --reservation=cns_nest --output={cluster.output} --error={cluster.error} --cpus-per-task={cluster.cpus-per-task} --ntasks={cluster.ntasks} --ntasks-per-node={cluster.ntasks-per-node} --time={cluster.time} --mem={cluster.mem}G"`

* disclaimer: conda is *only* used in this tutorial for convenience. to get optimal performance, use the module system and contact administrators to help with a system wide installation.
