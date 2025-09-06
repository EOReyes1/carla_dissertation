# Scaling CARLA simulations with High-Performance Computing for ADS 

This repository contains the source code and supplementary files for the dissertation "Scaling CARLA simulations with High-Performance Computing for ADS". The primary objective was to replicate a known ADS research Methodology and analyse its performance, reproducibility and its scalabilty in an HPC environment. 

The original repository can be found here: https://github.com/ADS-Testing/SAMOTA 


# Repository Content

/implementation/runner: Contains the modified Python files and Shell scripts that adapted the original SAMOTA methodology to run on the HPC. Files of interest include: runner2.py and runner_multi.py, pylot_runner2.sh and pylot_runner_multi.sh.

/implementation/scripts: Contains the modified shell scripts designed to run the CARLA simulator on the HPC, run_simulator.sh and run_simulator_multi.sh

pylot_improved.def: The definition file used to create the Apptainer container.

samota_run.sh and samota_multi.sh: The Slurm job scripts responsible for resource allocation and for running the jobs non-interactively on the HPC.


# How to Use

To use these files, a HPC environment using Linux is ideal. The system must contain Apptainer and Slurm software, along with any modules found in the job scripts: Anaconda etc.

1. Please refer to the README.md found in the original repository to set up everything, ignoring CARLA and Docker related tasks.

2. Build the container using Apptainer and pylot_improved.def - apptainer build [name of container].sif pylot_improved.def

3. As it was not possible to add the container to the repository, changes need to be made to some of the files, mainly the runner.py files and pylot_runner.sh files. Replace the original name of the container - pylot_improvedv2.sif - with the name of your container.

4. The paths used for the bind mounts will also be different. Please ensure that host directory paths are corrected to your host directory paths.


# Additional Information

For a detailed analysis and discussion of the project's findings, please refer to the complete dissertation.

Author: [Owen Reyes]
