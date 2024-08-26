# Energy transfer models

The energy transfer process can be modelled for a particular configuration of donor and acceptor ions with the following exponential function 
here $t$ is time, $\gamma_r$ is the radiative decay rate, and $\gamma_{tr,j}$ is the energy transfer rate for this configuration. Assuming a single-step multipole-multipole interaction (currently, the only model implemented), $\gamma_{tr,j}$ may be modelled as a sum over the transfer rates to all acceptors $\gamma_{tr,j}$ takes the form: 

$$\gamma_{tr,j} = C_{cr} \sum_i \left(\frac{R_0}{R_i}\right)^s$$
$I_j(t) = e^{-(\gamma_r + \gamma_{tr,j})t}$
Here $R_i$ is the distance between donor and acceptor, $C_{cr}$ is the energy-transfer rate to an acceptor at $R_0$ the nearest-neighbour distance, and $s$ depends on the type of multipole-multipole interaction ($s$ = 6, 8, 10 for dipole-dipole, dipole-quadrupole and quadrupole-quadrupole interactions respectively). The term $\sum_i \left(\frac{R_0}{R_i}\right)^s$ forms the basis of our Monte Carlo simulation; we will refer to this as our interaction component. The lifetime for an ensemble of donors can be modelled by averaging over many possible configurations of donors and acceptors:

$$I(t) =\frac{1}{n} \sum_{j=1}^n  e^{-(\gamma_{r} + \gamma_{tr,j})t}$$

Where $n$ is the number of unique random configurations. We can also define an average energy transfer rate $\gamma_{av}$ defined as:
$$\frac{1}{n}\sum_{j=1}^n \gamma_{tr,j}$$
This is a useful value for comparing hosts at a similar concentration. 
