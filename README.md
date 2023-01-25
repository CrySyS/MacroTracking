# MacroTracking for CAN logs

This repository contains code for our paper [Privacy pitfalls of releasing in-vehicle network data](https://doi.org/10.1016/j.vehcom.2022.100565).

If you use this software, please cite our paper using the following format:

```
@article{GAZDAG2023100565,
    title = {Privacy pitfalls of releasing in-vehicle network data},
    journal = {Vehicular Communications},
    volume = {39},
    pages = {100565},
    year = {2023},
    issn = {2214-2096},
    doi = {https://doi.org/10.1016/j.vehcom.2022.100565},
    url = {https://www.sciencedirect.com/science/article/pii/S2214209622001127},
    author = {András Gazdag and Szilvia Lestyán and Mina Remeli and Gergely Ács and Tamás Holczer and Gergely Biczók}
}
```


## Execution of the code

Run the `main.py` file from the `src` folder.

## Input

The repository contains a sample CAN trace for testing purposes.

## Output folder contents

- `location.log`: the reconstructed trajectory for a CAN log
- `distance_measured.log`: the distance between a trajectory and the ground truth
- `trace.html`: the reconstructed trace visualization
