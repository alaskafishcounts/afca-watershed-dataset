# AFCA Integration Guide for Watershed Dataset

## Overview

This guide explains how to integrate the AFCA Watershed Dataset with the Alaska Fish Count App (AFCA). The dataset provides water quality, temperature, flow, and watershed boundary data for Alaska salmon monitoring locations.

## Repository Structure

```
afca-watershed-dataset/
├── data/
│   ├── 01-master/          # Master configuration files
│   ├── 02-watersheds/      # Watershed boundary data
│   ├── 03-temperature/     # Temperature monitoring data
│   ├── 04-quality/         # Water quality parameters
│   └── 05-flow/            # Stream flow measurements
├── manifest.json           # Dataset manifest for AFCA integration
└── docs/                   # Documentation and integration guides
```

## Data Loading in AFCA App

### 1. Load Manifest

```javascript
// Load the watershed dataset manifest
const manifest = await fetch('https://raw.githubusercontent.com/alaskafishcounts/afca-watershed-dataset/main/manifest.json');
const watershedManifest = await manifest.json();

// Access organized data structure
const locationData = watershedManifest.organized[locationId];
```

### 2. Load Temperature Data

```javascript
// Load temperature data for a specific location and year
const tempUrl = `https://raw.githubusercontent.com/alaskafishcounts/afca-watershed-dataset/main/${locationData.temperature[year]}`;
const tempResponse = await fetch(tempUrl);
const tempData = await tempResponse.json();

// Access temperature data
const dailyTemps = tempData.data; // Array of {date, temperature_c, quality}
const stats = tempData.statistics; // {mean, min, max, count}
```

### 3. Load Flow Data

```javascript
// Load flow data for a specific location and year
const flowUrl = `https://raw.githubusercontent.com/alaskafishcounts/afca-watershed-dataset/main/${locationData.flow[year]}`;
const flowResponse = await fetch(flowUrl);
const flowData = await flowResponse.json();

// Access flow data
const dailyFlows = flowData.data; // Array of {date, flow_cfs, quality}
const stats = flowData.statistics; // {mean, min, max, count}
```

### 4. Load Water Quality Data

```javascript
// Load water quality data for a specific location and year
const qualityUrl = `https://raw.githubusercontent.com/alaskafishcounts/afca-watershed-dataset/main/${locationData.quality[year]}`;
const qualityResponse = await fetch(qualityUrl);
const qualityData = await qualityResponse.json();

// Access water quality data
const weeklyQuality = qualityData.data; // Array of {date, ph, dissolved_oxygen_mg_l, turbidity_ntu, conductivity_us_cm, quality}
```

### 5. Load Watershed Boundary Data

```javascript
// Load watershed boundary data for a location
const watershedUrl = `https://raw.githubusercontent.com/alaskafishcounts/afca-watershed-dataset/main/${locationData.watershed}`;
const watershedResponse = await fetch(watershedUrl);
const watershedData = await watershedResponse.json();

// Access watershed data
const drainageArea = watershedData.drainage_area_sq_miles;
const tributaries = watershedData.primary_tributaries;
const boundary = watershedData.watershed_boundary; // GeoJSON FeatureCollection
```

## Data Integration with Fish Counts

### Temperature vs Fish Counts Correlation

```javascript
// Load both fish count and temperature data
const fishCounts = await loadFishCountData(locationId, year);
const temperatureData = await loadTemperatureData(locationId, year);

// Correlate temperature with fish counts
const correlationData = fishCounts.map(fishDay => {
    const tempDay = temperatureData.data.find(temp => temp.date === fishDay.date);
    return {
        date: fishDay.date,
        fishCount: fishDay.count,
        temperature: tempDay?.temperature_c || null
    };
});
```

### Flow vs Fish Counts Analysis

```javascript
// Analyze flow patterns with fish migration
const flowData = await loadFlowData(locationId, year);
const fishCounts = await loadFishCountData(locationId, year);

// Find peak flow periods
const peakFlows = flowData.data.filter(day => day.flow_cfs > flowData.statistics.mean * 1.5);

// Correlate with fish counts
const peakFlowFishCounts = peakFlows.map(flowDay => {
    const fishDay = fishCounts.find(fish => fish.date === flowDay.date);
    return {
        date: flowDay.date,
        flow: flowDay.flow_cfs,
        fishCount: fishDay?.count || 0
    };
});
```

## Chart Integration

### Temperature Chart

```javascript
// Create temperature chart for AFCA location page
const tempChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: temperatureData.data.map(d => d.date),
        datasets: [{
            label: 'Water Temperature (°C)',
            data: temperatureData.data.map(d => d.temperature_c),
            borderColor: 'rgb(75, 192, 192)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            tension: 0.1
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: false,
                title: {
                    display: true,
                    text: 'Temperature (°C)'
                }
            }
        }
    }
});
```

### Flow Chart

```javascript
// Create flow chart for AFCA location page
const flowChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: flowData.data.map(d => d.date),
        datasets: [{
            label: 'Stream Flow (ft³/s)',
            data: flowData.data.map(d => d.flow_cfs),
            borderColor: 'rgb(54, 162, 235)',
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            tension: 0.1
        }]
    },
    options: {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: 'Flow (ft³/s)'
                }
            }
        }
    }
});
```

## Error Handling

```javascript
async function loadWatershedData(locationId, year, parameter) {
    try {
        const manifest = await fetch('https://raw.githubusercontent.com/alaskafishcounts/afca-watershed-dataset/main/manifest.json');
        const watershedManifest = await manifest.json();
        
        const locationData = watershedManifest.organized[locationId];
        if (!locationData) {
            throw new Error(`Location ${locationId} not found in watershed dataset`);
        }
        
        const dataUrl = `https://raw.githubusercontent.com/alaskafishcounts/afca-watershed-dataset/main/${locationData[parameter][year]}`;
        const response = await fetch(dataUrl);
        
        if (!response.ok) {
            throw new Error(`Failed to load ${parameter} data for location ${locationId}, year ${year}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error loading watershed data:', error);
        return null;
    }
}
```

## Performance Considerations

### Caching Strategy

```javascript
// Cache watershed data in localStorage
const CACHE_KEY = 'afca_watershed_data';
const CACHE_DURATION = 24 * 60 * 60 * 1000; // 24 hours

async function getCachedWatershedData(locationId, year, parameter) {
    const cacheKey = `${CACHE_KEY}_${locationId}_${year}_${parameter}`;
    const cached = localStorage.getItem(cacheKey);
    
    if (cached) {
        const { data, timestamp } = JSON.parse(cached);
        if (Date.now() - timestamp < CACHE_DURATION) {
            return data;
        }
    }
    
    const data = await loadWatershedData(locationId, year, parameter);
    if (data) {
        localStorage.setItem(cacheKey, JSON.stringify({
            data,
            timestamp: Date.now()
        }));
    }
    
    return data;
}
```

### Lazy Loading

```javascript
// Load watershed data only when needed
const watershedDataLoader = {
    async loadTemperatureData(locationId, year) {
        if (!this.temperatureCache) {
            this.temperatureCache = {};
        }
        
        const key = `${locationId}_${year}`;
        if (!this.temperatureCache[key]) {
            this.temperatureCache[key] = await loadWatershedData(locationId, year, 'temperature');
        }
        
        return this.temperatureCache[key];
    }
};
```

## Testing Integration

### Test Data Loading

```javascript
// Test watershed data integration
async function testWatershedIntegration() {
    const testLocationId = 410; // Kenai River
    const testYear = 2023;
    
    try {
        // Test manifest loading
        const manifest = await fetch('https://raw.githubusercontent.com/alaskafishcounts/afca-watershed-dataset/main/manifest.json');
        console.log('Manifest loaded:', await manifest.json());
        
        // Test temperature data
        const tempData = await loadWatershedData(testLocationId, testYear, 'temperature');
        console.log('Temperature data loaded:', tempData);
        
        // Test flow data
        const flowData = await loadWatershedData(testLocationId, testYear, 'flow');
        console.log('Flow data loaded:', flowData);
        
        // Test water quality data
        const qualityData = await loadWatershedData(testLocationId, testYear, 'quality');
        console.log('Water quality data loaded:', qualityData);
        
        console.log('Watershed integration test passed!');
    } catch (error) {
        console.error('Watershed integration test failed:', error);
    }
}
```

## Next Steps

1. **Test Integration**: Use the test functions to verify data loading
2. **Add Charts**: Integrate temperature and flow charts into AFCA location pages
3. **Correlation Analysis**: Add fish count vs water parameter correlation features
4. **Real Data**: Replace sample data with actual USGS/EPA data
5. **More Locations**: Expand dataset to include all AFCA monitoring locations
6. **Historical Data**: Add historical water data for trend analysis
