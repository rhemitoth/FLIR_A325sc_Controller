import rpy2.robjects as robjects
from rpy2.robjects.packages import SignatureTranslatedAnonymousPackage

# Import the R script into Python
robjects.r.source("/Users/rhemitoth/Documents/PhD/Cembra/FLIR_A325sc_Controller/Solar_Radiation_Functions_for_Python.R")

# Access the function
get_solrad = robjects.r['get_solar_radiation']

# Call the R function
result = get_solrad(dt = "2024-07-11 12:11:00", lat = 46, lon = 11, slope = 40, slope_aspect =  90, hemisphere = "north", ATMOSPHERIC_TRANSMISSIVITY = 0.8)
print(result)  # Output: [7]


