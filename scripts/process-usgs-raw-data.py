#!/usr/bin/env python3
"""
AFCA USGS Raw Data Processing Script
Processes downloaded USGS raw data files into AFCA format
"""

import os
import json
from datetime import datetime
from pathlib import Path

def get_working_directory():
    """Return the working directory for local storage"""
    return "."

class USGSRawDataProcessor:
    def __init__(self):
        self.base_dir = get_working_directory()
        self.raw_data_dir = f"{self.base_dir}/raw-data"
        self.output_dir = f"{self.base_dir}/data"
        
    def process_raw_usgs_file(self, raw_file_path):
        """Process a single raw USGS data file"""
        print(f"Processing: {os.path.basename(raw_file_path)}")
        
        try:
            with open(raw_file_path, 'r') as f:
                data = json.load(f)
            
            # Extract time series data
            if 'value' in data and 'timeSeries' in data['value']:
                time_series = data['value']['timeSeries']
                
                # Process each time series
                for series in time_series:
                    self._process_time_series(series)
                
                return True
            else:
                print(f"  No time series data found in {raw_file_path}")
                return False
                
        except Exception as e:
            print(f"  Error processing {raw_file_path}: {e}")
            return False
    
    def _process_time_series(self, series):
        """Process a single time series from USGS data"""
        try:
            # Extract station information
            source_info = series['sourceInfo']
            site_code = source_info['siteCode'][0]['value']
            site_name = source_info['siteName']
            
            # Extract variable information
            variable = series['variable']
            variable_code = variable['variableCode'][0]['value']
            variable_name = variable['variableName']
            
            # Extract values
            values = series['values'][0]['value']
            
            # Map variable codes to AFCA parameters
            parameter_map = {
                '00060': 'flow',
                '00010': 'temperature', 
                '00065': 'stage',
                '00095': 'conductivity',
                '00094': 'dissolved_oxygen',
                '00076': 'turbidity',
                '00400': 'ph'
            }
            
            parameter = parameter_map.get(variable_code, 'unknown')
            
            if parameter == 'unknown':
                print(f"  Unknown parameter code: {variable_code} ({variable_name})")
                return
            
            # Map station codes to AFCA location IDs
            station_map = {
                '15276000': 410,  # Kenai River
                '15290000': 411,  # Russian River
                '15284000': 412,  # Moose River
                '15292000': 413   # Killey River
            }
            
            location_id = station_map.get(site_code)
            if not location_id:
                print(f"  Unknown station code: {site_code}")
                return
            
            # Process values into daily data
            daily_data = self._convert_to_daily_data(values, parameter)
            
            if daily_data:
                # Group by year
                yearly_data = {}
                for day in daily_data:
                    year = day['date'][:4]
                    if year not in yearly_data:
                        yearly_data[year] = []
                    yearly_data[year].append(day)
                
                # Save yearly data
                for year, year_data in yearly_data.items():
                    self._save_processed_data(location_id, site_name, parameter, year, year_data)
            
        except Exception as e:
            print(f"  Error processing time series: {e}")
    
    def _convert_to_daily_data(self, values, parameter):
        """Convert USGS values to daily data format"""
        daily_data = {}
        
        for value in values:
            try:
                # Extract date and value
                date_time = value['dateTime']
                date = date_time[:10]  # YYYY-MM-DD
                value_str = value['value']
                
                # Skip missing values
                if value_str == '-999999' or value_str == '':
                    continue
                
                # Convert to float
                try:
                    numeric_value = float(value_str)
                except ValueError:
                    continue
                
                # Determine quality
                qualifiers = value.get('qualifiers', [])
                quality = 'good'
                for qualifier in qualifiers:
                    if qualifier['qualifierCode'] in ['P', 'e', 'A']:
                        quality = 'fair'
                    elif qualifier['qualifierCode'] in ['R', 'S']:
                        quality = 'poor'
                
                # Group by date
                if date not in daily_data:
                    daily_data[date] = []
                
                daily_data[date].append({
                    'value': numeric_value,
                    'quality': quality,
                    'datetime': date_time
                })
                
            except (KeyError, ValueError) as e:
                continue
        
        # Calculate daily averages
        daily_averages = []
        for date, day_values in daily_data.items():
            if day_values:
                # Calculate average value
                values_list = [v['value'] for v in day_values]
                avg_value = sum(values_list) / len(values_list)
                
                # Determine overall quality
                qualities = [v['quality'] for v in day_values]
                if all(q == 'good' for q in qualities):
                    quality = 'good'
                elif any(q == 'poor' for q in qualities):
                    quality = 'poor'
                else:
                    quality = 'fair'
                
                # Create output format based on parameter
                if parameter == 'flow':
                    output_value = {'flow_cfs': round(avg_value, 2)}
                elif parameter == 'temperature':
                    output_value = {'temperature_c': round(avg_value, 2)}
                elif parameter == 'stage':
                    output_value = {'stage_ft': round(avg_value, 2)}
                elif parameter == 'conductivity':
                    output_value = {'conductivity_us_cm': round(avg_value, 0)}
                elif parameter == 'dissolved_oxygen':
                    output_value = {'dissolved_oxygen_mg_l': round(avg_value, 2)}
                elif parameter == 'turbidity':
                    output_value = {'turbidity_ntu': round(avg_value, 2)}
                elif parameter == 'ph':
                    output_value = {'ph': round(avg_value, 2)}
                else:
                    continue
                
                daily_averages.append({
                    'date': date,
                    **output_value,
                    'quality': quality
                })
        
        return sorted(daily_averages, key=lambda x: x['date'])
    
    def _save_processed_data(self, location_id, location_name, parameter, year, year_data):
        """Save processed data in AFCA format"""
        # Calculate statistics
        if parameter == 'flow':
            values = [d['flow_cfs'] for d in year_data]
            unit = 'ft³/s'
        elif parameter == 'temperature':
            values = [d['temperature_c'] for d in year_data]
            unit = '°C'
        elif parameter == 'stage':
            values = [d['stage_ft'] for d in year_data]
            unit = 'ft'
        elif parameter == 'conductivity':
            values = [d['conductivity_us_cm'] for d in year_data]
            unit = 'µS/cm'
        elif parameter == 'dissolved_oxygen':
            values = [d['dissolved_oxygen_mg_l'] for d in year_data]
            unit = 'mg/L'
        elif parameter == 'turbidity':
            values = [d['turbidity_ntu'] for d in year_data]
            unit = 'NTU'
        elif parameter == 'ph':
            values = [d['ph'] for d in year_data]
            unit = 'pH units'
        else:
            return
        
        if values:
            stats = {
                'mean': round(sum(values) / len(values), 2),
                'min': round(min(values), 2),
                'max': round(max(values), 2),
                'count': len(values)
            }
            
            # Create AFCA format data
            afca_data = {
                'location_id': location_id,
                'location_name': location_name,
                'year': int(year),
                'parameter': parameter,
                'unit': unit,
                'data': year_data,
                'statistics': stats,
                'source': 'USGS Stream Gauge Network',
                'last_updated': datetime.now().isoformat()
            }
            
            # Determine output directory and filename
            if parameter in ['flow']:
                output_dir = f"{self.output_dir}/05-flow"
            elif parameter in ['temperature']:
                output_dir = f"{self.output_dir}/03-temperature"
            elif parameter in ['stage']:
                output_dir = f"{self.output_dir}/06-stage"
            elif parameter in ['conductivity', 'dissolved_oxygen', 'turbidity', 'ph']:
                output_dir = f"{self.output_dir}/04-quality"
            else:
                return
            
            os.makedirs(output_dir, exist_ok=True)
            output_file = f"{output_dir}/location-{location_id}-{year}.json"
            
            with open(output_file, 'w') as f:
                json.dump(afca_data, f, indent=2)
            
            print(f"  Saved {parameter} data for {location_name} {year}: {len(year_data)} days")
    
    def process_all_raw_files(self):
        """Process all raw USGS data files"""
        if not os.path.exists(self.raw_data_dir):
            print("Raw data directory not found")
            return
        
        raw_files = [f for f in os.listdir(self.raw_data_dir) if f.startswith('usgs_') and f.endswith('.json')]
        
        if not raw_files:
            print("No raw USGS data files found")
            return
        
        print(f"Found {len(raw_files)} raw USGS data files to process")
        
        success_count = 0
        for raw_file in raw_files:
            raw_file_path = f"{self.raw_data_dir}/{raw_file}"
            if self.process_raw_usgs_file(raw_file_path):
                success_count += 1
        
        print(f"\nProcessed {success_count}/{len(raw_files)} raw files successfully")
    
    def update_manifest(self):
        """Update manifest.json with processed data"""
        print("Updating manifest with processed USGS data...")
        
        manifest_path = f"{self.base_dir}/manifest.json"
        
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        # Count files in each directory
        total_files = 0
        locations_covered = set()
        years_covered = set()
        organized = {}
        
        for data_dir in ["02-watersheds", "03-temperature", "04-quality", "05-flow", "06-stage"]:
            data_path = f"{self.output_dir}/{data_dir}"
            if os.path.exists(data_path):
                files = [f for f in os.listdir(data_path) if f.endswith('.json')]
                total_files += len(files)
                
                # Extract location IDs and years from filenames
                for filename in files:
                    if "location-" in filename:
                        parts = filename.replace(".json", "").split("-")
                        if len(parts) >= 3:
                            try:
                                location_id = int(parts[1])
                                locations_covered.add(location_id)
                                
                                year = int(parts[2])
                                years_covered.add(year)
                                
                                # Build organized structure
                                if str(location_id) not in organized:
                                    organized[str(location_id)] = {
                                        "watershed": f"data/02-watersheds/location-{location_id}.json",
                                        "temperature": {},
                                        "flow": {},
                                        "quality": {},
                                        "stage": {}
                                    }
                                
                                # Add file to organized structure
                                if data_dir == "03-temperature":
                                    organized[str(location_id)]["temperature"][str(year)] = f"data/03-temperature/location-{location_id}-{year}.json"
                                elif data_dir == "05-flow":
                                    organized[str(location_id)]["flow"][str(year)] = f"data/05-flow/location-{location_id}-{year}.json"
                                elif data_dir == "04-quality":
                                    organized[str(location_id)]["quality"][str(year)] = f"data/04-quality/location-{location_id}-{year}.json"
                                elif data_dir == "06-stage":
                                    organized[str(location_id)]["stage"][str(year)] = f"data/06-stage/location-{location_id}-{year}.json"
                                        
                            except ValueError:
                                continue
        
        # Update manifest statistics
        manifest["statistics"]["total_files"] = total_files
        manifest["statistics"]["locations_covered"] = len(locations_covered)
        manifest["statistics"]["years_covered"] = sorted(list(years_covered))
        manifest["last_updated"] = datetime.now().isoformat()
        manifest["organized"] = organized
        
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"  Updated manifest.json with {total_files} files, {len(locations_covered)} locations, {len(years_covered)} years")

def main():
    """Main processing function"""
    print("AFCA USGS Raw Data Processing Script")
    print("====================================")
    
    processor = USGSRawDataProcessor()
    
    # Process all raw USGS data files
    processor.process_all_raw_files()
    
    # Update manifest
    processor.update_manifest()
    
    print("\nUSGS raw data processing complete!")
    print("\nNext steps:")
    print("1. Review processed data files")
    print("2. Validate data quality and completeness")
    print("3. Test AFCA app integration")
    print("4. Add more data sources and locations")

if __name__ == "__main__":
    main()
