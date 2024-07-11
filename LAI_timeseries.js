// Define the location (latitude and longitude) and time range
var point = ee.Geometry.Point([11.190009999999999,46.130961999999997]); // Replace with your coordinates
var startDate = '2024-06-01';
var endDate = '2024-07-11';

// Load Sentinel-2 surface reflectance data
var dataset = ee.ImageCollection('COPERNICUS/S2_SR')
                .filterDate(startDate, endDate)
                .filterBounds(point)
                .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
                .select(['B4', 'B8']); // Red and NIR bands

// Function to calculate NDVI
var calculateNDVI = function(image) {
  var ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI');
  return image.addBands(ndvi);
};

// Apply the function to the dataset
var withNDVI = dataset.map(calculateNDVI);

// Function to estimate LAI from NDVI
// Note: This is a simplified empirical model for demonstration purposes
var ndviToLAI = function(ndvi) {
  return ndvi.multiply(3.618).subtract(0.118).rename('LAI'); // Example linear relationship
};

// Function to calculate LAI at the point location
var calculateLAI = function(image) {
  var ndvi = image.select('NDVI');
  var lai = ndviToLAI(ndvi);
  var laiValue = lai.reduceRegion({
    reducer: ee.Reducer.mean(),
    geometry: point,
    scale: 10
  }).get('LAI');
  
  return ee.Feature(null, {
    'date': image.date().format('YYYY-MM-dd'),
    'LAI': laiValue
  });
};

// Map the function over the dataset
var laiAtPoint = withNDVI.map(calculateLAI).filter(ee.Filter.notNull(['LAI']));

// Convert the result to a FeatureCollection
var laiTimeSeries = ee.FeatureCollection(laiAtPoint);

// Print the result
print(laiTimeSeries);

// Check if the collection is empty
var laiCount = laiTimeSeries.size();
print('Number of LAI entries:', laiCount);

// Export the result as a CSV file if there is data
if (laiCount.gt(0).getInfo()) {
  Export.table.toDrive({
    collection: laiTimeSeries,
    description: 'LAI_TimeSeries',
    fileFormat: 'CSV',
    folder: 'LAI'
  });
} else {
  print('No LAI data available for the specified location and time range.');
}
