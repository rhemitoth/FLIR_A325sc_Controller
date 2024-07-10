# ================== Summary =======================

## The script RadianceToTemp.py is used to converts the raw measurements from the FLIR camera to units of temperature (degrees Celcius).
## As input, this script accepts tiffs of raw data obtained from a thermal camera. 
## The tiffs should be saved using this file format "file-YYYYMMDD-HHMMSS" with the date and time that the image was captured in the filename. 

# ================================ Modules ===================================

import imageio.v2 as imageio
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from datetime import datetime
import platform

# ============================== Read in Images =============================

def tiffs_to_numpy_arrays(directory_path):

    """
    Reads all TIFF files in the given directory and converts them to numpy arrays.

    Args:
    directory_path (str): The path to the directory containing the TIFF files.

    Returns:
    dict: A dictionary where the keys are the filenames and the values are a list containing the
    corresponding numpy arrays and the date that the data was collected. 

    """
    numpy_arrays = {}

    for filename in os.listdir(directory_path):
        if filename.lower().endswith('.tiff') or filename.lower().endswith('.tif'):
            file_path = os.path.join(directory_path, filename)
            dt = get_image_datetime(file_path)
            img = imageio.imread(file_path)
            numpy_array = np.array(img)
            numpy_arrays[filename] = [numpy_array,dt]

    return numpy_arrays


# ============================ Get Image Metadata ==============================

def get_image_datetime(file_path):
    try:
        if platform.system() == 'Windows':
            # On Windows, use getctime for creation time
            creation_time = os.path.getctime(file_path)
        else:
            # On Unix-like systems, use stat for creation time if available
            stat = os.stat(file_path)
            creation_time = getattr(stat, 'st_birthtime', stat.st_ctime)
        
        # Convert the timestamps to datetime objects
        creation_datetime = datetime.fromtimestamp(creation_time)
        
        return creation_datetime
    
    except Exception as e:
        return f'Error retrieving file dates: {e}'

# ========================= Get Weather Data =========================================

def csv_to_df(filepath):

    """

    This function reads in a csv and converts it to a pandas dataframe

    Args:
    filepath (string): filepath of the csv

    Returns:
    df: pandas dataframe

    """

    # read in csv and convert to pandas
    df = pd.read_csv(filepath)
    # return the result
    return(df)


def get_Ta(weather_dat, datetime):
    """
    Finds the air temperature at the time of image capture.
    
    Args:
    weather_dat (pandas df): Pandas dataframe of weather data
    datetime (datetime): Timestamp of the image capture
    
    Returns:
    float: Air temperature at the time of image capture
    """
    given_time = pd.to_datetime(datetime)
    weather_dat['timestamp'] = pd.to_datetime(weather_dat['timestamp'])
    weather_dat['time_diff'] = (weather_dat['timestamp'] - given_time).abs()
    closest_row = weather_dat.loc[weather_dat['time_diff'].idxmin()]
    air_temp = closest_row['TA']
    return air_temp

def get_RH(weather_dat, datetime):
    """
    Finds the humidity at the time of image capture.
    
    Args:
    weather_dat (pandas df): Pandas dataframe of weather data
    datetime (datetime): Timestamp of the image capture
    
    Returns:
    float: Humidity at the time of image capture
    """
    given_time = pd.to_datetime(datetime)
    weather_dat['timestamp'] = pd.to_datetime(weather_dat['timestamp'])
    weather_dat['time_diff'] = (weather_dat['timestamp'] - given_time).abs()
    closest_row = weather_dat.loc[weather_dat['time_diff'].idxmin()]
    hum = closest_row['RH']
    return hum

# ========================= Longwave Radiation from the Surroundings ==================

def get_LW():

    """

    This function is used to estimate the total longwave radiation of the surroundings (downward and upward facing).

    This code for this function adapted from the functions Ld() and Lu() contained in the Thermimage R package:
    https://cran.r-project.org/package=Thermimage

    Args:
    air_temp (float): The temperature of the air in degress celcius
    hum (float): The humidity of the air in percent RH
    ground_temp (float): The temperature of the ground surface in degrees celcius
    e_ground (float): The emissivity of the ground surface
    cc (float): Fractional cloud cover


    """

    return(200)

# ========================= Convert from Raw FLIR Data to Temp =====================

def raw_to_temp(
    raw_array, 
    # Properties of the surroundings
    rh,
    t_air,
    t_win,
    LW,
    e_refl = 0.95,
    # Emissivity of target
    e_target = 0.95, 
    # Radiative transfer coefficients
    X = 1.9, 
    a1 = 0.01, 
    a2 = 0.01, 
    b1 = 0, 
    b2 = -0.01,
    # Planck Function Coefficients
    R1 = 17070.73, 
    R2 = 0.01160998, 
    B = 1437.2, 
    F = 1, 
    O = -7393, 
    # Enclosure Properties
    trans_win = 1,
    refl_win = 0,
    # Distance between the sensor and the targer
    dist = 1.415
    ):

    """

    Converts a NumPy array of raw data values to a NumPy array of surface temperature values. See Johnston et al. 2021 Appendix A for a full description of how to convert
    from radiance to temperature. 

    Args:
    rad_array (numpy array): NumPy array of radiance values.
    e_target (float):  Emissivity of the subject (usually 0.95 for an animal).
    X (float): Radiative transfer coefficeint. Can be obtained by navigating to the features tab of the SpinView desktop application from the FLIR Spinnaker SDK. 
    a1 (float): Radiative transfer coefficient. Can be obtained by navigating to the features tab of the SpinView desktop application from the FLIR Spinnaker SDK. 
    a2 (float): Radiative transfer coefficient. Can be obtained by navigating to the features tab of the SpinView desktop application from the FLIR Spinnaker SDK. 
    b1 (float): Radiative transfer coefficient. Can be obtained by navigating to the features tab of the SpinView desktop application from the FLIR Spinnaker SDK. 
    b2 (float): Radiative transfer coefficient. Can be obtained by navigating to the features tab of the SpinView desktop application from the FLIR Spinnaker SDK. 
    R1 (float): Planck function coefficient. Can be obtained by navigating to the features tab of the SpinView desktop application from the FLIR Spinnaker SDK. 
    R2 (float): Planck function coefficient. Can be obtained by navigating to the features tab of the SpinView desktop application from the FLIR Spinnaker SDK. 
    B (float): Planck function coefficient. Can be obtained by navigating to the features tab of the SpinView desktop application from the FLIR Spinnaker SDK. 
    F (float): Planck function coefficient. Can be obtained by navigating to the features tab of the SpinView desktop application from the FLIR Spinnaker SDK. 
    O (float): Planck function coefficient. Can be obtained by navigating to the features tab of the SpinView desktop application from the FLIR Spinnaker SDK. 
    trans_win (float): Transmissivity of the enclosure window (0-1).
    refl_win (float): Reflectivity of the enclosure window (0-1).
    dist (float): Distance the camera and the target (m).
    rh (float): Relative humidity of the air (0-1).
    t_air (float): Temperature of the air (Celcius).
    t_win (float): Temperature of the enclosure window (Celcius).
    LW (float): Longwave radiation of the surroundings (W/m2).
    e_refl (float): Emissivity of the surroundings (0-1).

    Returns:
    temp_array: NumPy array of temperature values

    """

    # Stefan-Boltzman Constant
    sigma = 5.670374419e-8

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
    phi_target = (raw_array/e_target/trans_air/trans_win) - (phi_refl*e_refl*(1-e_target)/e_target)-(phi_air*(1-trans_air)/e_target/trans_air)-(phi_win*(1-refl_win-trans_win)/e_target/trans_air/trans_win)

    # Target Temperature
    t_target_K = B/np.log(R1/(R2*(phi_target+O)+F)) # kelvin
    t_target = t_target_K - 273.15

    # Return result
    return(t_target)

# ========================= Save Results =====================

def save_np_as_tiff(np_array, outdir, filename):

    """

    This function saves a numpy array as a tiff.

    Args:

    np_array (numpy array): numpy array that will be saved as a tiff
    outdir (string): directory where the tiff will be saved
    filename (string): Name of the image. I like to use the date and time that the image was captured. 

    Returns: 

    Nothing. Just saves a tiff to your computer. 

    """

    # Build the file name
    filepath = outdir + filename

    # Save the image
    imageio.imwrite(filepath, np_array)

def save_np_as_csv(np_array,outdir,filename):

    """

    This function saves a numpy array as a CSV.

    Args:

    np_array (numpy array): numpy array that will be saved as a CSV
    outdir (string): directory where the CSV will be saved
    filename (string): Name of the CSV. I like to use the date and time that the image was captured. 

    Returns: 

    Nothing. Just saves a CSV to your computer. 

    """

    # Build the file name
    filepath = outdir + filename

    # Save the csv
    np.savetxt(filepath, np_array,  
              delimiter = ",")

# ========================= Main Code =========================================

def main():

    # Build a dictionary of numpy arrays from all of the tiff files in a directory

    raw_arrays = tiffs_to_numpy_arrays("/Users/rhemitoth/Documents/PhD/Cembra/R/data_raw/cembra_0708")

    # Load weather data

    weather_df = csv_to_df("/Users/rhemitoth/Documents/PhD/Cembra/FLIR_A325sc_Controller/radiance2temp_test_data/weather.csv")

    # Loop through the radiance arrays and convert from radiance to temperature

    num_raw_arrays = len(raw_arrays)

    temp_arrays = {}

    timestamps = []

    for key in raw_arrays:

    	print(key)

        # get the timestamp of the image

        dt = raw_arrays[key][1] 

        # get the air temperature at the time the image was taken

        air_temperature = get_Ta(weather_dat = weather_df, datetime = dt)

        # get the humidity at the time the image was taken 

        humidity = get_RH(weather_dat = weather_df, datetime = dt)

        # get the longwave radiation of the surroundings at the time of image capture
        longwave = get_LW()

        # Convert raw FLIR data to units of temperature

        temp_array = raw_to_temp(raw_array = raw_arrays[key][0], rh = humidity, t_air = air_temperature, t_win = air_temperature, LW = longwave)

        # Save results 

        fname = "file-"+str(dt).replace(" ","_").replace("-","").replace(":","")+".csv"

        save_np_as_csv(np_array = temp_array, outdir = "/Users/rhemitoth/Documents/PhD/Cembra/FLIR_A325sc_Controller/radiance2temp_test_data/results/",filename = fname)

        # Plot results

        plot_data = temp_array
        plt.imshow(plot_data, interpolation='nearest')
        plt.colorbar()
        plt.show()

        #temp_arrays[key] = [temp_array,dt]

if __name__ == '__main__':
    main()



