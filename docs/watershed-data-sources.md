# Watershed Data Sources for AFCA Integration

## Primary Data Sources

### 1. USGS Watershed Boundary Dataset (WBD)
- **URL**: https://www.usgs.gov/national-hydrography/watershed-boundary-dataset
- **Description**: Comprehensive dataset defining hydrologic unit boundaries
- **Format**: Shapefile, GeoJSON
- **Coverage**: All of Alaska
- **Update Frequency**: Annual
- **Integration**: Watershed boundary data for AFCA locations

### 2. USGS Stream Gauge Network
- **URL**: https://waterdata.usgs.gov
- **Description**: Real-time stream flow and temperature data
- **Parameters**: Flow (ft³/s), Temperature (°C), Stage (ft)
- **Coverage**: Major Alaska rivers and streams
- **Update Frequency**: Real-time (15-minute intervals)
- **Integration**: Temperature and flow data for salmon monitoring

### 3. EPA National Aquatic Resource Surveys
- **URL**: https://www.epa.gov/national-aquatic-resource-surveys
- **Description**: Water quality assessments and biological data
- **Parameters**: pH, dissolved oxygen, turbidity, nutrients
- **Coverage**: Selected Alaska water bodies
- **Update Frequency**: Periodic surveys
- **Integration**: Water quality parameters for salmon habitat

### 4. ADF&G Water Quality Monitoring
- **URL**: https://www.adfg.alaska.gov
- **Description**: Alaska-specific water quality monitoring
- **Parameters**: Temperature, pH, dissolved oxygen, conductivity
- **Coverage**: Fish monitoring locations
- **Update Frequency**: Seasonal
- **Integration**: Direct correlation with fish count data

## Research Publications

### Canadian Journal of Fisheries and Aquatic Sciences 2016
- **DOI**: 10.1139/cjfas-2016-0076
- **URL**: https://cdnsciencepub.com/doi/full/10.1139/cjfas-2016-0076
- **Status**: Pending download and text extraction
- **Key Data**: Watershed temperature and flow data for Alaska salmon streams

## Data Integration Strategy

### Phase 1: Stream Gauge Data
1. Download real-time data from USGS stream gauges
2. Map gauge stations to AFCA location IDs
3. Create temperature and flow time series
4. Generate standardized JSON format

### Phase 2: Watershed Boundaries
1. Download WBD data for Alaska
2. Extract watershed boundaries for AFCA locations
3. Calculate drainage areas and characteristics
4. Create GeoJSON format for mapping

### Phase 3: Water Quality Data
1. Download EPA and ADF&G water quality data
2. Extract parameters relevant to salmon
3. Map to AFCA monitoring locations
4. Create quality assessment records

### Phase 4: Research Integration
1. Extract data from research papers
2. Parse temperature and flow measurements
3. Map to AFCA location IDs
4. Create historical data records

## Next Steps

1. **Download Research Papers**: Get PDFs from academic sources
2. **Extract Text**: Convert PDFs to text for data extraction
3. **Parse Data**: Use scripts to extract temperature, flow, and quality data
4. **Map Locations**: Connect to AFCA location IDs
5. **Create JSON Files**: Generate standardized data files
6. **Update Manifest**: Include new data in repository manifest
7. **Test Integration**: Verify data loads correctly in AFCA app
