// Define the point of interest (replace with your coordinates)
var point = ee.Geometry.Point([11.190009999999999,46.130961999999997]); 

// Define a date range for the time series (change as needed)
var startDate = '2024-07-01';
var endDate = '2024-07-11';

// Load MODIS MCD43A3 surface albedo data
var collection = ee.ImageCollection('MODIS/061/MCD43A3')
                  .filterDate(startDate, endDate);

// Function to calculate and export time series of surface albedo
var exportAlbedoTimeSeries = function(point, startDate, endDate) {
  // Filter the collection to the point of interest
  var albedoCollection = collection.filterBounds(point)
                                   .select('Albedo_BSA_shortwave');

  // Extract time series data at the point
  var albedoTimeSeries = albedoCollection.map(function(image) {
    var date = ee.Date(image.get('system:time_start')).format('YYYY-MM-dd');
    var albedo = image.reduceRegion({
      reducer: ee.Reducer.mean(),
      geometry: point,
      scale: 500,  // Resolution in meters
      maxPixels: 1e9
    }).get('Albedo_BSA_shortwave');
    
    // Ensure albedo is not null before scaling
    var scaledAlbedo = ee.Algorithms.If(
      albedo,
      ee.Number(albedo).multiply(0.001),
      null
    );
    
    // Create a feature with the date and scaled albedo
    return ee.Feature(null, {
      'date': date,
      'albedo': scaledAlbedo
    });
  }).filter(ee.Filter.notNull(['albedo'])); // Filter out null albedo values

  // Export the feature collection as a CSV file to Google Drive
  Export.table.toDrive({
    collection: albedoTimeSeries,
    description: 'albedo_time_series',
    fileFormat: 'CSV',
    selectors: ['date', 'albedo'],
    folder: 'albedo'
  });
};

// Run the function
exportAlbedoTimeSeries(point, startDate, endDate);

// Print a message
print('Exporting albedo time series...');
