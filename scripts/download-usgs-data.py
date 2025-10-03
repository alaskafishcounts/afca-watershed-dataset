#!/usr/bin/env python3
"""
AFCA USGS Data Download Script
Downloads real-time and historical data from USGS stream gauges
"""

import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

def get_working_directory():
    """Return the working directory for local storage"""
    return "."

class USGSDataDownloader:
    def __init__(self):
        self.base_url = "https://waterservices.usgs.gov/nwis"
        self.base_dir = get_working_directory()
        self.raw_data_dir = f"{self.base_dir}/raw-data"
        os.makedirs(self.raw_data_dir, exist_ok=True)
        
    def get_station_info(self, station_id):
        """Get station information from USGS"""
        url = f"{self.base_url}/site"
        params = {
            'format': 'json',
            'sites': station_id,
            'siteOutput': 'expanded'
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if 'value' in data and 'timeSeries' in data['value']:
                return data['value']['timeSeries']
            return None
            
        except Exception as e:
            print(f"Error getting station info for {station_id}: {e}")
            return None
    
    def download_instantaneous_data(self, station_id, start_date, end_date, parameters=None):
        """Download instantaneous (15-minute) data from USGS"""
        if parameters is None:
            parameters = ['00060', '00010', '00065']  # Flow, Temperature, Stage
        
        url = f"{self.base_url}/iv"
        params = {
            'format': 'json',
            'sites': station_id,
            'startDT': start_date,
            'endDT': end_date,
            'parameterCd': ','.join(parameters),
            'siteStatus': 'all'
        }
        
        try:
            print(f"Downloading instantaneous data for station {station_id}...")
            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            # Save raw data
            raw_file = f"{self.raw_data_dir}/usgs_instantaneous_{station_id}_{start_date}_{end_date}.json"
            with open(raw_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"  Saved raw data: {raw_file}")
            return data
            
        except Exception as e:
            print(f"  Error downloading instantaneous data: {e}")
            return None
    
    def download_daily_data(self, station_id, start_date, end_date, parameters=None):
        """Download daily data from USGS"""
        if parameters is None:
            parameters = ['00060', '00010', '00065']  # Flow, Temperature, Stage
        
        url = f"{self.base_url}/dv"
        params = {
            'format': 'json',
            'sites': station_id,
            'startDT': start_date,
            'endDT': end_date,
            'parameterCd': ','.join(parameters),
            'siteStatus': 'all'
        }
        
        try:
            print(f"Downloading daily data for station {station_id}...")
            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            # Save raw data
            raw_file = f"{self.raw_data_dir}/usgs_daily_{station_id}_{start_date}_{end_date}.json"
            with open(raw_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"  Saved raw data: {raw_file}")
            return data
            
        except Exception as e:
            print(f"  Error downloading daily data: {e}")
            return None
    
    def download_water_quality_data(self, station_id, start_date, end_date):
        """Download water quality data from USGS"""
        # Common water quality parameters
        parameters = [
            '00010',  # Temperature
            '00095',  # Specific conductance
            '00094',  # Dissolved oxygen
            '00076',  # Turbidity
            '00400',  # pH
            '00403',  # pH, field
            '00405',  # pH, lab
        ]
        
        url = f"{self.base_url}/iv"
        params = {
            'format': 'json',
            'sites': station_id,
            'startDT': start_date,
            'endDT': end_date,
            'parameterCd': ','.join(parameters),
            'siteStatus': 'all'
        }
        
        try:
            print(f"Downloading water quality data for station {station_id}...")
            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            # Save raw data
            raw_file = f"{self.raw_data_dir}/usgs_water_quality_{station_id}_{start_date}_{end_date}.json"
            with open(raw_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"  Saved raw data: {raw_file}")
            return data
            
        except Exception as e:
            print(f"  Error downloading water quality data: {e}")
            return None
    
    def get_available_parameters(self, station_id):
        """Get available parameters for a station"""
        url = f"{self.base_url}/site"
        params = {
            'format': 'json',
            'sites': station_id,
            'siteOutput': 'expanded'
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            parameters = []
            if 'value' in data and 'timeSeries' in data['value']:
                for series in data['value']['timeSeries']:
                    param_code = series['variable']['variableCode'][0]['value']
                    param_name = series['variable']['variableName']
                    parameters.append({
                        'code': param_code,
                        'name': param_name
                    })
            
            return parameters
            
        except Exception as e:
            print(f"Error getting parameters for station {station_id}: {e}")
            return []
    
    def download_alaska_stations_data(self):
        """Download data for all Alaska stations"""
        # Alaska stream gauge stations
        alaska_stations = [
            {"station_id": "15276000", "location_id": 410, "location_name": "Kenai River at Soldotna, AK"},
            {"station_id": "15290000", "location_id": 411, "location_name": "Russian River near Cooper Landing, AK"},
            {"station_id": "15284000", "location_id": 412, "location_name": "Moose River near Sterling, AK"},
            {"station_id": "15292000", "location_id": 413, "location_name": "Killey River near Sterling, AK"}
        ]
        
        # Download data for the last 2 years
        end_date = datetime.now()
        start_date = end_date - timedelta(days=730)  # 2 years
        
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        print(f"Downloading data from {start_str} to {end_str}")
        
        for station in alaska_stations:
            print(f"\nProcessing station: {station['location_name']} ({station['station_id']})")
            
            # Get available parameters
            parameters = self.get_available_parameters(station['station_id'])
            print(f"  Available parameters: {len(parameters)}")
            for param in parameters[:5]:  # Show first 5 parameters
                print(f"    {param['code']}: {param['name']}")
            
            # Download instantaneous data
            self.download_instantaneous_data(station['station_id'], start_str, end_str)
            
            # Download daily data
            self.download_daily_data(station['station_id'], start_str, end_str)
            
            # Download water quality data
            self.download_water_quality_data(station['station_id'], start_str, end_str)
    
    def create_station_summary(self):
        """Create a summary of downloaded stations"""
        summary = {
            "download_date": datetime.now().isoformat(),
            "stations": [],
            "total_files": 0
        }
        
        # Count downloaded files
        if os.path.exists(self.raw_data_dir):
            files = [f for f in os.listdir(self.raw_data_dir) if f.endswith('.json')]
            summary["total_files"] = len(files)
            
            # Group files by station
            stations = {}
            for file in files:
                if file.startswith('usgs_'):
                    parts = file.split('_')
                    if len(parts) >= 3:
                        station_id = parts[2]
                        if station_id not in stations:
                            stations[station_id] = []
                        stations[station_id].append(file)
            
            # Create station summaries
            for station_id, files in stations.items():
                station_summary = {
                    "station_id": station_id,
                    "files": files,
                    "file_count": len(files)
                }
                summary["stations"].append(station_summary)
        
        # Save summary
        summary_file = f"{self.raw_data_dir}/download_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\nDownload summary saved: {summary_file}")
        print(f"Total files downloaded: {summary['total_files']}")
        print(f"Stations processed: {len(summary['stations'])}")

def main():
    """Main download function"""
    print("AFCA USGS Data Download Script")
    print("==============================")
    
    downloader = USGSDataDownloader()
    
    # Download data for Alaska stations
    downloader.download_alaska_stations_data()
    
    # Create summary
    downloader.create_station_summary()
    
    print("\nUSGS data download complete!")
    print("\nNext steps:")
    print("1. Review downloaded raw data files")
    print("2. Run process-water-data.py to convert to AFCA format")
    print("3. Validate processed data quality")
    print("4. Test AFCA app integration")

if __name__ == "__main__":
    main()
