![](nest-and-snakemake.png)

# Introduction to the simulation of structurally detailed large-scale neuronal networks

Tutorial at HBP Student Conference 2020 in Pisa.

Tutors: Sandra Diaz, Alper Yegenoglu, Alexander van Meegen

## Installation

We recommend using a conda environment to get all necessary dependencies.
After [installing conda](https://conda.io/docs/user-guide/install/index.html), create a new environment and activate it:
```
conda env create -f environment.yml
conda activate HBPSC2020_NEST
```

If nest is not found in jupyter notebooks check if the jupyter kernel is correct:
```
jupyter kernelspec list
``` 
If there is no kernel corresponding to the current environment, install it:
```
python -m ipykernel install --prefix $CONDA_PREFIX
```

## Acknowledgements

This tutorials extensively makes use of previous NEST tutorials by
* Hannah Bos
* David Dahmen
* Moritz Deger
* Jochen Martin Eppler
* Espen Hagen
* Abigail Morrison
* Jannis Schuecker
* Johanna Senk
* Tom Tetzlaff
* Sacha van Albada
