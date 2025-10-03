#!/usr/bin/env python3
"""
AFCA Watershed Dataset Source Download Script
Downloads water data from various government and research sources
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path

def get_working_directory():
    """Return the working directory for local storage"""
    return "."

def download_usgs_watershed_data():
    """Download USGS Watershed Boundary Dataset information"""
    print("Downloading USGS Watershed Boundary Dataset information...")
    
    # USGS Watershed Boundary Dataset API endpoint
    usgs_url = "https://www.usgs.gov/national-hydrography/watershed-boundary-dataset"
    
    try:
        response = requests.get(usgs_url, timeout=30)
        if response.status_code == 200:
            print(f"  Successfully accessed USGS WBD: {usgs_url}")
            print("  Note: Actual data download requires specific API calls or manual download")
        else:
            print(f"  Error accessing USGS WBD: {response.status_code}")
    except Exception as e:
        print(f"  Error downloading USGS data: {e}")

def download_epa_water_quality_data():
    """Download EPA National Aquatic Resource Surveys information"""
    print("Downloading EPA National Aquatic Resource Surveys information...")
    
    epa_url = "https://www.epa.gov/national-aquatic-resource-surveys"
    
    try:
        response = requests.get(epa_url, timeout=30)
        if response.status_code == 200:
            print(f"  Successfully accessed EPA NARS: {epa_url}")
            print("  Note: Actual data download requires specific API calls or manual download")
        else:
            print(f"  Error accessing EPA NARS: {response.status_code}")
    except Exception as e:
        print(f"  Error downloading EPA data: {e}")

def download_usgs_stream_gauge_data():
    """Download USGS Stream Gauge Network information"""
    print("Downloading USGS Stream Gauge Network information...")
    
    usgs_gauge_url = "https://waterdata.usgs.gov/nwis/rt"
    
    try:
        response = requests.get(usgs_gauge_url, timeout=30)
        if response.status_code == 200:
            print(f"  Successfully accessed USGS Stream Gauge Network: {usgs_gauge_url}")
            print("  Note: Actual data download requires specific gauge station queries")
        else:
            print(f"  Error accessing USGS Stream Gauge Network: {response.status_code}")
    except Exception as e:
        print(f"  Error downloading USGS stream gauge data: {e}")

def create_alaska_stream_gauge_list():
    """Create a list of Alaska stream gauge stations"""
    print("Creating Alaska stream gauge station list...")
    
    # Known Alaska stream gauge stations for salmon monitoring
    alaska_gauges = [
        {
            "station_id": "15276000",
            "station_name": "Kenai River at Soldotna, AK",
            "latitude": 60.4878,
            "longitude": -151.0583,
            "afca_location_id": 410,
            "parameters": ["flow", "temperature", "stage"],
            "usgs_url": "https://waterdata.usgs.gov/nwis/uv?site_no=15276000"
        },
        {
            "station_id": "15290000",
            "station_name": "Russian River near Cooper Landing, AK",
            "latitude": 60.4833,
            "longitude": -149.8333,
            "afca_location_id": 411,
            "parameters": ["flow", "temperature", "stage"],
            "usgs_url": "https://waterdata.usgs.gov/nwis/uv?site_no=15290000"
        },
        {
            "station_id": "15284000",
            "station_name": "Moose River near Sterling, AK",
            "latitude": 60.5167,
            "longitude": -150.8667,
            "afca_location_id": 412,
            "parameters": ["flow", "temperature", "stage"],
            "usgs_url": "https://waterdata.usgs.gov/nwis/uv?site_no=15284000"
        }
    ]
    
    base_dir = get_working_directory()
    output_file = f"{base_dir}/data/01-master/alaska-stream-gauges.json"
    
    gauge_data = {
        "version": "1.0.0",
        "last_updated": datetime.now().isoformat(),
        "description": "Alaska stream gauge stations for salmon monitoring",
        "total_stations": len(alaska_gauges),
        "stations": alaska_gauges,
        "data_sources": [
            {
                "source": "USGS Stream Gauge Network",
                "url": "https://waterdata.usgs.gov",
                "description": "Real-time stream flow and temperature data"
            }
        ]
    }
    
    with open(output_file, "w") as f:
        json.dump(gauge_data, f, indent=2)
    
    print(f"  Created Alaska stream gauge list: {output_file}")
    print(f"  Total stations: {len(alaska_gauges)}")

def create_watershed_research_notes():
    """Create research notes for watershed data sources"""
    print("Creating watershed research notes...")
    
    base_dir = get_working_directory()
    output_file = f"{base_dir}/docs/watershed-data-sources.md"
    
    research_notes = """# Watershed Data Sources for AFCA Integration

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
"""
    
    with open(output_file, "w") as f:
        f.write(research_notes)
    
    print(f"  Created watershed research notes: {output_file}")

def main():
    """Main download function"""
    print("Downloading watershed data sources...")
    
    download_usgs_watershed_data()
    download_epa_water_quality_data()
    download_usgs_stream_gauge_data()
    create_alaska_stream_gauge_list()
    create_watershed_research_notes()
    
    print("\nWatershed source download complete!")
    print("\nNext steps:")
    print("1. Manually download research papers from academic sources")
    print("2. Extract text from PDFs using pdftotext or online tools")
    print("3. Run extract-watershed-data.py to parse research data")
    print("4. Download actual USGS stream gauge data for Alaska stations")
    print("5. Create watershed boundary files for AFCA locations")

if __name__ == "__main__":
    main()
