<h1 align="center">PYET-MC</h1>
<p align="center">
  <img width="400" height="400" alt="pyet_logo" src="https://github.com/JaminMartin/pyet-mc/blob/main/images/pyet_logov1.svg">
</p>

<h2 align="center">A library to model energy transfer between lanthanide ions</h2>
<h3 align="center">Get in contact or follow research related to this project</h3>
<p align="center">
    <a href="https://github.com/JaminMartin"><img height="50" src="https://github.com/JaminMartin/pyet-mc/blob/main/images/github.svg" alt="Github"></a>
    &nbsp;
    <a href="https://www.linkedin.com/in/jamin-martin-87448a167/"><img height="50" src="https://github.com/JaminMartin/pyet-mc/blob/main/images/linkedin.svg" alt="LinkedIn"></a>
    &nbsp;
    <a href="https://orcid.org/0000-0002-7204-231X"><img height="50" src="https://github.com/JaminMartin/pyet-mc/blob/main/images/ORCID_iD.svg" alt="ORCID"></a>
    &nbsp;
    <a href="https://www.researchgate.net/profile/Jamin-Martin"><img height="50" src="https://github.com/JaminMartin/pyet-mc/blob/main/images/ResearchGate_icon.svg" alt="ResearchGate"></a>
    &nbsp;
</p>

## Table of Contents
- [Introduction](#introduction)
- [Documentation](#documentation)
- [Referencing this project](#referencing-this-project)  
- [License](#license)

# Introduction
Collection of tools for modelling the energy transfer processes in lanthanide-doped materials. 

Contains functions for visualising crystal structure around a central donor ion, subroutines for nearest neighbour probabilities and monte-carlo based multi-objective fitting for energy transfer rates. This package aims to streamline the fitting process while providing useful tools to obtain quick structural information. The core function of this library is the ability to simultaneously fit lifetime data for various concentrations to tie down energy transfer rates more accurately. This allows one to decouple certain dataset features, such as signal offset/amplitude, from physical parameters, such as radiative and energy transfer rates. This is all handled by a relatively straightforward API wrapping the Scipy Optimise library. This library is based on the scripts initially written for studying multi-polar interactions between samarium ions in KY<sub>3</sub>F<sub>10</sub>

# Documentation

The documentation for this project, e.g. how to install and use the project can be found here: https://jaminmartin.github.io/pyet-mc/

# Referencing this project
To reference this project, you can use the citation tool in the About info of this repository. Details can also be found in the .cff file in the source code. 
# License
The project is licensed under the GNU GENERAL PUBLIC LICENSE.
