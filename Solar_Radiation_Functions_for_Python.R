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


# Generate Timestamps -----------------------------------------------------

# This function generates an hourly series of time-stamps between a specified start and end time
#
# Args:
# start_ts (string): The start point of the time-series ("YYYY-MM-DD hh:mm:ss")
# end_ts (string): The end point of the time-series ("YYYY-MM-DD hh:mm:ss")
#
# Returns:
# ts (list): A list of strings

get_timestamps <- function(start_ts, end_ts){
  
  # Convert strings to datetime objects
  
  start_ts_dtobj <- ymd_hms(start_ts)
  end_ts_dtobj <- ymd_hms(end_ts)
  
  # Generate hourly timeseries
  ts <- seq(from = start_ts_dtobj,
                    to = end_ts_dtobj,
                    by = "hour")
  
  # Return result
  return(ts)
  
}


# Get Albedo from Timeseries ----------------------------------------------

# This function returns the closest record of albedo in time from a timeseries of albedo
#
#Arguments:
# albedo_ts (dataframe): albedo time series. Should contain a column called "date" and a column called "albedo". Date should be formatted as "YYYY-MM-DD".
# datetime (string): Timestamp that will be matched to a record in the albedo timeseries ("YYYY-MM-DD hh:mm:ss")
#
# Returns:
# albedo (float)

get_albedo <- function(dt, albedo_ts) {
  
  # convert timeseries dates to datetime object
  albedo_ts$date <- ymd(albedo_ts$date)
  
  # Extract date from dt
  dt_date <- date(dt)
  
  # Calculate the absolute time difference
  albedo_ts$timediff <- abs(albedo_ts$date - dt_date)
  
  # Find the row with the minimum time difference
  closest_record <- albedo_ts[which.min(albedo_ts$timediff),]
  
  # Get the albedo
  albedo <- closest_record$albedo
  
  return(albedo)
}


# Get Atmospheric Transmissivity Timeseries -------------------------------

# This function returns the closest record of atmospheric transmissivity in time from a timeseries of atmospheric transmissivity
#
#Arguments:
# atrans_ts (dataframe): atmospheric transmissivity time series. Should contain a column called "date" and a column called "clear_sky_index". Date should be formatted as "YYYY-MM-DD".
# datetime (string): Timestamp that will be matched to a record in the atmospheric transmissivity timeseries ("YYYY-MM-DD hh:mm:ss")
#
# Returns:
# atrans (float)

get_atmospheric_transmissivity <- function(dt, atrans_ts) {
  
  # Calculate the absolute time difference
  atrans_ts$timediff <- abs(atrans_ts$time - dt)
  
  # Find the row with the minimum time difference
  closest_record <- atrans_ts[which.min(atrans_ts$timediff),]
  
  # Get the albedo
  atrans <- closest_record$clear_sky_index
  
  return(atrans)
}


# Get DOY -----------------------------------------------------------------

# This function calculates the day of the year from a timestamp
#
# Arguments:
# timestamp (datetime object): Date and time in the format "YYYY-MM-DD hh:mm:ss"
#
# Returns:
# doy (integer): the day of year

get_doy <- function(timestamp){
  
  # Extract the day of the year
  doy <- yday(timestamp)
  
  # Return the result
  doy <- as.numeric(doy)
  return(doy)
}


# Get hour ----------------------------------------------------------------

# This function calculates the hour of the day from a timestamp
#
# Arguments:
# timestamp (datetime object): Date and time in the format "YYYY-MM-DD hh:mm:ss"
#
# Returns:
# hour (integer): the hour of the day (0 - 24)

get_hour <- function(timestamp){
  
  # Extract the hour
  hour <- hour(timestamp)
  
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
  SLOPE_ASPECT <- degrees_to_radians(SLOPE_ASPECT)
  
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
    
    zenith_updated <- acos(a*b+c*d*e)
    
  }
  else{
    zenith_updated <- zenith
  }
  
  res <- data.frame(
    ZENITH_ORIG = zenith,
    ZENITH_UPDATED = zenith_updated,
    SUN_AZIMUTH = sun_azimuth
  )
  
  return(res)
  print(res)
  
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


# Solar Radiation Time Series ---------------------------------------------

solarad_timeseries <- function(timestamps,
                               LAT,
                               LON,
                               SLOPE,
                               SLOPE_ASPECT,
                               HEMISPHERE,
                               atmospheric_transmissivity,
                               elev,
                               albedo){
  
  # Calculate solar radiation timeseries

  solrads <- sapply(X = timestamps, 
                    FUN = get_solar_radiation,
                    lat = LAT,
                    lon = LON,
                    slope = SLOPE,
                    slope_aspect = SLOPE_ASPECT,
                    hemisphere = HEMISPHERE,
                    ATMOSPHERIC_TRANSMISSIVITY = atmospheric_transmissivity,
                    ELEV = elev,
                    ALBEDO = albedo)
  
  # Convert result to dataframe
  res <- tibble(ts = timestamps,
                solar_radiaiton = as.numeric(solrads))
  
  return(res)
  
}


# Generate Solar Radiation Time Series ----------------------------------------------------

# Use this section of the code to generate your solar radiation time series and
# export the results as a csv

# 1) Generate your time stamps

start_time <- "2024-07-10 00:00:00" # replace with your start time
end_time <- "2024-07-16 00:00:00" # replace with your end time
timestamps <- get_timestamps(start_ts = start_time, end_ts = end_time)

# 2) Get albedo timeseries

# Replace path with the location on your computer where the albedo timeseries is stored
# You can generate albedo using the GEE script albedo_timeseries.js on the GitHub

albedo_ts_raw <- read_csv("/Users/rhemitoth/Library/CloudStorage/GoogleDrive-rhemitoth@g.harvard.edu/My Drive/Cembra/albedo/albedo_time_series.csv")
albedos <- sapply(X = timestamps, FUN = get_albedo, albedo_ts = albedo_ts_raw)

# 3) Get atmospheric transmissivity timeseries

# Replace path with the location on your computer where the atmospheric transmissivity timeseries is stored
# You can generate atmospheric transmissivty values using the GEE script atmospheric_transmissivty_timeseries.js on the GitHub

atrans_ts_raw <- read_csv("/Users/rhemitoth/Library/CloudStorage/GoogleDrive-rhemitoth@g.harvard.edu/My Drive/Cembra/Atmospheric_Transmissivity/ClearSkyIndexTimeSeries.csv")
atrans <- sapply(X = timestamps, FUN = get_atmospheric_transmissivity, atrans_ts = atrans_ts_raw)

# 4) Set inputs for solar radiation calculations

lattitude <- 46.130961999999997 # latitude where solar radiation will be calculated (degrees)
longitude <- 11.190009999999999 # longitude where solar radiation will be calculated (degrees)
SLOPE <- 1.017573714256287 # slope of the ground at the location where solar radiation will be calculated (degrees). You can calculate this using your method of choice (ArcGIS, QGIS, terra package etc.)
aspect <- 92.496437072753906 # aspect of the slope at the location where solar radiation will be calculated (degrees). You can calculate this using your method of choice (ArcGIS, QGIS, terra package etc.)
elev <- 900.943969726562614 # elevation at the location where solar radiation will be calculated. You can calculate this using your method of choice (ArcGIS, QGIS, terra package etc.)
HEMISPHERE <- "north" # hemisphere of the earth at the location where solar radiation will be calculated

# 5) Get solar radiation timeseries

solrad_timeseries1 <- lapply(1:length(timestamps), function(x) {
  get_solar_radiation(dt = timestamps[x],
                      lat = lattitude,
                      lon = longitude,
                      slope = SLOPE,
                      slope_aspect = aspect,
                      hemisphere = HEMISPHERE,
                      ATMOSPHERIC_TRANSMISSIVITY = atrans[x],
                      ELEV = elev,
                      ALBEDO = albedos[x])
})

solrad_timeseries2 <- do.call("rbind", lapply(solrad_timeseries1, data.frame))

solar_radiation_timeseries <- tibble(timestamp = timestamps,
                                     solar_radiation = solrad_timeseries2$X..i..)

# 6) Export result

write.csv(x = solar_radiation_timeseries,
          file = "/Users/rhemitoth/Library/CloudStorage/GoogleDrive-rhemitoth@g.harvard.edu/My Drive/Cembra/solar_radiation/solar_radiation.csv")


