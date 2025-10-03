# AFCA Watershed Dataset

A comprehensive dataset of Alaska watershed and water quality data for integration with the Alaska Fish Count App (AFCA).

## Overview

This repository contains organized water data including:
- Watershed boundaries and drainage areas
- Water temperature monitoring data
- Water quality parameters
- Stream flow measurements
- Research data from scientific publications

## Repository Structure

```
afca-watershed-dataset/
├── data/
│   ├── 01-master/          # Master configuration files
│   ├── 02-watersheds/      # Watershed boundary data
│   ├── 03-temperature/     # Temperature monitoring data
│   ├── 04-quality/         # Water quality parameters
│   └── 05-flow/            # Stream flow measurements
├── scripts/                # Data processing and integration scripts
├── docs/                   # Documentation and research notes
├── pdf-source-materials/   # Source PDFs and research papers
└── manifest.json           # Dataset manifest for AFCA integration
```

## Data Sources

### Primary Sources
- USGS Watershed Boundary Dataset (WBD)
- EPA National Aquatic Resource Surveys
- ADF&G Water Quality Monitoring
- USGS Stream Gauge Network

### Research Publications
- Canadian Journal of Fisheries and Aquatic Sciences
- ADF&G Technical Publications
- USGS Scientific Investigations Reports

## Integration with AFCA

This dataset is designed to integrate with the Alaska Fish Count App through:
- Standardized JSON data formats
- Manifest-driven data loading
- Location-based data organization
- Temporal data alignment with fish count periods

## Usage

### For AFCA App Integration
```javascript
// Load watershed data for a specific location
const watershedData = await fetch('https://raw.githubusercontent.com/alaskafishcounts/afca-watershed-dataset/main/data/02-watersheds/location-410.json');
```

### For Research and Analysis
```python
# Process temperature data
import json
with open('data/03-temperature/kenai-river-2023.json') as f:
    temp_data = json.load(f)
```

## Contributing

1. Follow AFCA data standards
2. Include source attribution
3. Validate JSON structure
4. Update manifest.json

## License

Public domain data - Alaska Fish Count App Project
