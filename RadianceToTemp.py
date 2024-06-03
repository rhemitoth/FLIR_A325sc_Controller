# packages
import imageio
import math
import matplotlib.pyplot as plt
import numpy as np

# read in image
fpath = ("C:/Users/user/Documents/FLIR/Python/pics/file-20240531-221409.tiff")
imarray = imageio.imread(fpath)
print(imarray)

############## Parameters ##############

# Emissivity of target
e_target = 0.95

# Radiative transfer coefficients
X = 1.9
a1 = 0.01
a2 = 0.01
b1 = 0
b2 = -0.01

# Planck function coefficients
R1 = 17070.73
R2 = 0.01160998
B = 1437.2 # from flir
F = 1
O = -7393
# Transmissivity 
trans_win = 1
X = 1.9 # atmospheric trans X

# Refelctivity of enclosure window
refl_win = 0

# Stefan-Boltzman const
sigma = 5.670374419e-8

# Distance between sensor and target
dist = 1

# Weather
rh = 0.3 # relative humidity
t_air = 27.2 # air temperature
t_win = 23 # enclosure window temperature
LW = 200 # Longwave radiation of surroundings

# Surroundings
e_refl = 1 # emissivity of surroundings

############# Calculations ######################

# air water vapor concentration
C_H2O = rh*math.exp(1.5587+6.939*(10**-2)*t_air-2.7816*(10**-4)*(t_air**2)+6.8455*(10**-7)*(t_air**3))

# transmissivity of air
trans_air = X*math.exp(-math.sqrt(dist)*(a1+b1*math.sqrt(C_H2O)))+(1-X)*math.exp(-math.sqrt(dist)*(a1+b2*math.sqrt(C_H2O)))

# Sky temperature
t_refl = (LW/sigma)**(0.25)

# Energy of window
phi_win = (R1/R2*(1/(math.exp(B/t_win)-F)))-O

# Energy of air
phi_air = (R1/R2*(1/(math.exp(B/t_air)-F)))-O

# Reflected energy
phi_refl = (R1/R2*(1/(math.exp(B/t_refl)-F)))-O

# Energy of target
phi_target = (imarray/e_target/trans_air/trans_win) - (phi_refl*e_refl*(1-e_target)/e_target)-(phi_air*(1-trans_air)/e_target/trans_air)-(phi_win*(1-refl_win-trans_win)/e_target/trans_air/trans_win)

# Target Temperature
t_target_K = B/np.log(R1/(R2*(phi_target+O)+F)) # kelvin
t_target = t_target_K - 273.15
print(t_target)

# Save array as image
imageio.imwrite("result.tiff", t_target)