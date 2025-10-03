# AFCA Watershed Dataset Research Sources

## Primary Research Papers

### Canadian Journal of Fisheries and Aquatic Sciences 2016
- **URL**: https://cdnsciencepub.com/doi/full/10.1139/cjfas-2016-0076
- **Title**: [To be extracted from PDF]
- **Authors**: [To be extracted from PDF]
- **Year**: 2016
- **Key Data**: Watershed temperature and flow data for Alaska salmon streams
- **Status**: Pending download and text extraction

## USGS Data Sources

### Watershed Boundary Dataset (WBD)
- **URL**: https://www.usgs.gov/national-hydrography/watershed-boundary-dataset
- **Description**: Comprehensive dataset defining hydrologic unit boundaries
- **Format**: Shapefile, GeoJSON
- **Coverage**: All of Alaska
- **Update Frequency**: Annual

### Stream Gauge Network
- **URL**: https://waterdata.usgs.gov
- **Description**: Real-time stream flow and temperature data
- **Parameters**: Flow (ft³/s), Temperature (°C), Stage (ft)
- **Coverage**: Major Alaska rivers and streams
- **Update Frequency**: Real-time (15-minute intervals)

## EPA Data Sources

### National Aquatic Resource Surveys
- **URL**: https://www.epa.gov/national-aquatic-resource-surveys
- **Description**: Water quality assessments and biological data
- **Parameters**: pH, dissolved oxygen, turbidity, nutrients
- **Coverage**: Selected Alaska water bodies
- **Update Frequency**: Periodic surveys

## ADF&G Data Sources

### Water Quality Monitoring
- **URL**: https://www.adfg.alaska.gov
- **Description**: Alaska-specific water quality monitoring
- **Parameters**: Temperature, pH, dissolved oxygen, conductivity
- **Coverage**: Fish monitoring locations
- **Update Frequency**: Seasonal

## Data Integration Plan

### Phase 1: Research Paper Analysis
1. Download key research papers
2. Extract text from PDFs
3. Parse temperature and flow data
4. Map locations to AFCA location IDs

### Phase 2: USGS Data Integration
1. Download watershed boundary data
2. Extract stream gauge data for AFCA locations
3. Process temperature and flow time series
4. Create standardized JSON format

### Phase 3: EPA Data Integration
1. Download water quality survey data
2. Extract parameters relevant to salmon
3. Map to AFCA monitoring locations
4. Create quality assessment records

### Phase 4: ADF&G Data Integration
1. Access ADF&G water quality data
2. Integrate with existing fish count data
3. Create comprehensive water quality profiles
4. Establish data quality standards

## Data Quality Standards

### Temperature Data
- **Unit**: Celsius (°C)
- **Precision**: 0.1°C
- **Range**: 0-30°C
- **Quality Flags**: Good, Fair, Poor

### Flow Data
- **Unit**: Cubic feet per second (ft³/s)
- **Precision**: 1 ft³/s
- **Range**: 0-100,000 ft³/s
- **Quality Flags**: Good, Fair, Poor

### Water Quality Parameters
- **pH**: 6.0-9.0 range
- **Dissolved Oxygen**: >4 mg/L minimum
- **Turbidity**: <25 NTU preferred

## Integration with AFCA App

### Data Loading Pattern
```javascript
// Load watershed data for location
const watershedData = await fetch(
  'https://raw.githubusercontent.com/alaskafishcounts/afca-watershed-dataset/main/data/02-watersheds/location-410.json'
);

// Load temperature data for specific year
const tempData = await fetch(
  'https://raw.githubusercontent.com/alaskafishcounts/afca-watershed-dataset/main/data/03-temperature/location-410-2023.json'
);
```

### Manifest Structure
```json
{
  "organized": {
    "410": {
      "watershed": "data/02-watersheds/location-410.json",
      "temperature": {
        "2023": "data/03-temperature/location-410-2023.json",
        "2022": "data/03-temperature/location-410-2022.json"
      },
      "flow": {
        "2023": "data/05-flow/location-410-2023.json"
      },
      "quality": {
        "2023": "data/04-quality/location-410-2023.json"
      }
    }
  }
}
```

## Next Steps

1. **Download Research Papers**: Get PDFs from academic sources
2. **Extract Text**: Convert PDFs to text for data extraction
3. **Parse Data**: Use scripts to extract temperature, flow, and quality data
4. **Map Locations**: Connect to AFCA location IDs
5. **Create JSON Files**: Generate standardized data files
6. **Update Manifest**: Include new data in repository manifest
7. **Test Integration**: Verify data loads correctly in AFCA app
