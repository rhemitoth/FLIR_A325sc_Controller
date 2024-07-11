// Define the location (longitude, latitude)
var location = ee.Geometry.Point(-74.0060, 40.7128); // Example: New York City

// Define the time period of interest
var startDate = '2024-07-01';
var endDate = '2024-07-11';

// Load solar radiation data (global and extraterrestrial)
var solarRad = ee.ImageCollection('ECMWF/ERA5_LAND/HOURLY')
  .filterDate(startDate, endDate)
  .select('surface_net_solar_radiation', 'surface_solar_radiation_downwards');

// Function to calculate the clear-sky index (global radiation / extraterrestrial radiation)
var calculateClearSkyIndex = function(image) {
  var globalRad = image.select('surface_net_solar_radiation');
  var extraterrestrialRad = image.select('surface_solar_radiation_downwards');
  var clearSkyIndex = globalRad.divide(extraterrestrialRad);
  return clearSkyIndex.rename('clear_sky_index')
    .copyProperties(image, ['system:time_start']);
};

// Map over the image collection to apply the function
var clearSkyIndex = solarRad.map(calculateClearSkyIndex);

// Convert the ImageCollection to a FeatureCollection
var featureCollection = clearSkyIndex.map(function(image) {
  // Calculate mean value for the location
  var value = image.reduceRegion({
    reducer: ee.Reducer.mean(),
    geometry: location,
    scale: 1000 // Adjust scale as needed
  });
  
  // Extract time from image
  var time = image.get('system:time_start');
  
  // Convert time from milliseconds to Date object
  var date = ee.Date(time);
  
  // Format date as string (e.g., 'YYYY-MM-dd HH:mm:ss')
  var formattedDate = date.format('YYYY-MM-dd HH:mm:ss');
  
  // Create a feature with the formatted date and the calculated value
  var feature = ee.Feature(null, {
    'time': formattedDate,
    'clear_sky_index': value.get('clear_sky_index')
  });
  
  return feature;
});

// Export the FeatureCollection to Google Drive as CSV
Export.table.toDrive({
  collection: ee.FeatureCollection(featureCollection),
  description: 'ClearSkyIndexTimeSeries',
  fileFormat: 'CSV',
  folder: 'Atmospheric_Transmissivity'
});

// Print a link to the task
print('Exporting Clear Sky Index time series to Google Drive as CSV...');
