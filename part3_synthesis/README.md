# Synthesis: towards a real-world example

Now we combine all the tools and move towards a real-world example:
Simulating and analyzing a full-scale cortical neural network based on
anatomical (structural) data.

In an actual real-world example, many steps of the workflow concern the
data preprocessing. Here we leave this out for simplicity and build upon
an existing model:

Schmidt et al. (2018) Multi-scale account of the network structure of macaque visual cortex. Brain Structure and Function 223(3):1409-1435
Schmidt et al. (2018) A multi-scale layer-resolved spiking network model of resting-state dynamics in macaque visual cortical areas. PLOS CB 14(10):e1006359


## Tasks

* Understand the workflow
* How does the spiking activity look like?
  * Add a rule and make a script to produce rasterplots of the spiking activity.
* So far, we did not consider any transmission delays, in particular between areas.
  * Add transmission delays to the simulation.


## Notes

### TODO: HPC presentation

* parallelization
  * MPI, OpenMP
  * memory layout
  * RNG seeding
  * communication
* queuing / batch system
  * data retrieval / storage
* cluster.json, snakemake & SLURM
