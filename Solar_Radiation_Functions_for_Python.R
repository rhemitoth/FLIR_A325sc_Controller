## ---------------------------
##
## Script name: Sun functions
##
## Author: Rhemi Toth
##
## Date Created: 2024-07-11
##
## Email: rhemitoth@g.harvard.edu
##
## ---------------------------
##
## Notes: This script contains functions to estimate solar radiation at a point using
## resources from the TrenchR library
##
##
## ---------------------------


# Load Packages ----------------------------------------------------------

library(TrenchR)
library(tidyverse)
library(lubridate)

# Get DOY -----------------------------------------------------------------

# This function calculates the day of the year from a timestamp
#
# Arguments:
# timestamp (string): Date and time in the format "YYYY-MM-DD hh:mm:ss"
#
# Returns:
# doy (integer): the day of year

get_doy <- function(timestamp){
  
  # Convert string to a datetime object
  datetime_obj <- strptime(timestamp, format = "%Y-%m-%d %H:%M:%S")
  
  # Extract the day of the year
  doy <- yday(datetime_obj)
  
  # Return the result
  doy <- as.numeric(doy)
  return(doy)
}


# Get hour ----------------------------------------------------------------

# This function calculates the hour of the day from a timestamp
#
# Arguments:
# timestamp (string): Date and time in the format "YYYY-MM-DD hh:mm:ss"
#
# Returns:
# hour (integer): the hour of the day (0 - 24)

get_hour <- function(timestamp){
  
  # Convert string to a datetime object
  datetime_obj <- strptime(timestamp, format = "%Y-%m-%d %H:%M:%S")
  
  # Extract the hour
  hour <- hour(datetime_obj)
  
  # Return the result
  return(hour)
  
}

# Calculate Zenith Angle --------------------------------------------------

# This function calculates the zenith angle of the sun based on the day of the year,
# latitude, and longitude. If the slope is not flat, the function calls update_zenith
# to apply a correction to the zenith angle based on the slope of the ground.
# Corrections for the zenith angle are conducted using equations from
# "Underlying theory and equations of the NicheMapR microclimate model" (Kearney & Porter 2024)

# Arguments
# DOY (integer): Day of the year (1-365)
# LAT (float): Latitude
# LON (float): Longitude
# SLOPE (float): Slope of the ground surface in degrees
# SLOPE_ASPECT (float): Aspect of the slope in degrees
# HEMISHPHERE (text): Hemisphere of the location ("north" or "south")

get_zenith <- function(datetime,LAT,LON,SLOPE,SLOPE_ASPECT,HEMISPHERE){
  
  # Get the day of the year from the datetime
  DOY <- get_doy(datetime)
  
  # Get the hour of the day from the datetime
  HOUR <- get_hour(datetime)
  
  # Get the closest hour of the day from the datetime
  zenith <- zenith_angle(doy = DOY, lat = LAT, lon = LON, hour = HOUR)
  
  # Convert inputs to radians
  
  zenith <- degrees_to_radians(zenith)
  SLOPE <- degrees_to_radians(SLOPE)
  LAT <- degrees_to_radians(LAT)
  LON <- degrees_to_radians(LON)
  
  # Get ecpliptic longitude of earths orbit
  e <- 0.01675 # eccentricity of Earth's orbit
  w <- 2*pi/365
  ecliptic_longitude <- w * (DOY - 80) + 2 * e * (sin(w*DOY)-sin(w*80))
  
  # Get the solar declination angle
  solar_declination <- asin(0.39784993*sin(ecliptic_longitude))
  
  # Apply correction if location is not on flat ground
  
  if (SLOPE != 0){
    if(HEMISPHERE == "north"){
      a <- sin(LAT)
      b <- sin(90*pi/180-zenith)
      c <- sin(solar_declination)
      d <- cos(LAT)
      e <- cos(90*pi/180-zenith)
      sun_azimuth <- acos((a*b-c)/(d*e))
    }
    else{
      a <- sin(solar_declination)
      b <- sin(LAT)
      c <- sin(90*pi/180-zenith)
      d <- cos(LAT)
      e <- cos(90*pi/180-z)
      sun_azimuth <- acos((a-b*c)/(d*e))
    }
    
    a <- cos(zenith)
    b <- cos(SLOPE)
    c <- sin(zenith)
    d <- sin(SLOPE)
    e <- cos(sun_azimuth-SLOPE_ASPECT)
    
    zenith_updated <- a*b+c*d*e
    
  }
  else{
    zenith_updated <- NA
  }
  
  res <- data.frame(
    ZENITH_ORIG = zenith,
    ZENITH_UPDATED = zenith_updated,
    SUN_AZIMUTH = sun_azimuth
  )
  
  return(res)
  
}


# Calculate Solar Radiation -----------------------------------------------

# This function calculate the total solar radiation reaching a point on the Earth's surface, accounting for atmospheric transitivity, but not
# shading from vegetation (to do this you need to apply a correction using Beer's law).
# The function calls get_zenith() to compute zenith angles.
#
# Args:
# dt (string): Date and time in the format "YYYY-MM-DD hh:mm:ss"
# lat (float): Latitude in degrees
# lon (float): Longitude in degrees
# slope (float): slope of the ground surface in degrees
# slope_aspect (float): aspect of the ground slope in degrees
# hemisphere (text): hemisphere where solar radiation is being calculate ("north" or "south")
# ATMOSPHERIC_TRANSMISSIVITY (float): ratio of the global solar radiation measured at the surface to the total solar radiation at the top of the atmosphere. (0-1)
# ELEV (float): Elevation where solar radiation is being calculated in meters
# ALBEDO (float): albedo of the ground surface (0-1)
#
# Returns:
# solrad (float): Solar radiation reaching the ground surface in W/m2

get_solar_radiation <- function(dt,
                                lat,
                                lon,
                                slope,
                                slope_aspect,
                                hemisphere,
                                ATMOSPHERIC_TRANSMISSIVITY,
                                ELEV,
                                ALBEDO){
  # calculate the zenith
  zenith_df <- get_zenith(datetime = dt, LAT = lat, LON = lon, SLOPE = slope, SLOPE_ASPECT =  slope_aspect, HEMISPHERE = "north")
  zenith <- zenith_df$ZENITH_UPDATED[1]
  
  # calculate solar radiation
  
  doy <- get_doy(dt)
  
  solrad <- solar_radiation(doy = doy,
                            psi = zenith,
                            tau = ATMOSPHERIC_TRANSMISSIVITY,
                            elev = ELEV,
                            rho = ALBEDO)
  
  solrad <- sum(solrad) # summing the direct, diffuse, and reflected radiation
  
  # returning the result
  return(solrad)
  
}

# Test example:
# get_solar_radiation(dt = "2024-07-11 12:11:00", lat = 46, lon = 11, slope = 40,
#                     slope_aspect =  90, hemisphere = "north", ELEV = 100, ALBEDO = 0.1,
#                     ATMOSPHERIC_TRANSMISSIVITY = 0.8)