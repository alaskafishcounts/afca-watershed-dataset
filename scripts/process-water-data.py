#!/usr/bin/env python3
"""
AFCA Water Data Processing Pipeline
Converts raw water data from various sources into standardized JSON format
"""

import os
import json
import csv
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
import re

def get_working_directory():
    """Return the working directory for local storage"""
    return "."

class WaterDataProcessor:
    def __init__(self):
        self.base_dir = get_working_directory()
        self.output_dir = f"{self.base_dir}/data"
        self.raw_data_dir = f"{self.base_dir}/raw-data"
        os.makedirs(self.raw_data_dir, exist_ok=True)
        
    def process_usgs_stream_gauge_data(self, station_id, location_id, location_name, start_date, end_date):
        """Process USGS stream gauge data into AFCA format"""
        print(f"Processing USGS stream gauge data for {location_name} (Station: {station_id})")
        
        # USGS Water Services API endpoint
        base_url = "https://waterservices.usgs.gov/nwis/iv/"
        params = {
            'format': 'json',
            'sites': station_id,
            'startDT': start_date,
            'endDT': end_date,
            'parameterCd': '00060,00010,00065',  # Flow, Temperature, Stage
            'siteStatus': 'all'
        }
        
        try:
            response = requests.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Parse USGS JSON response
            if 'value' in data and 'timeSeries' in data['value']:
                time_series = data['value']['timeSeries']
                
                # Extract flow data
                flow_data = self._extract_usgs_parameter(time_series, '00060', 'Flow')
                # Extract temperature data
                temp_data = self._extract_usgs_parameter(time_series, '00010', 'Temperature')
                # Extract stage data
                stage_data = self._extract_usgs_parameter(time_series, '00065', 'Stage')
                
                # Process and save data
                self._save_usgs_data(location_id, location_name, 'flow', flow_data)
                self._save_usgs_data(location_id, location_name, 'temperature', temp_data)
                self._save_usgs_data(location_id, location_name, 'stage', stage_data)
                
                return True
            else:
                print(f"  No data found for station {station_id}")
                return False
                
        except Exception as e:
            print(f"  Error processing USGS data: {e}")
            return False
    
    def _extract_usgs_parameter(self, time_series, parameter_code, parameter_name):
        """Extract specific parameter data from USGS time series"""
        for series in time_series:
            if series['variable']['variableCode'][0]['value'] == parameter_code:
                values = series['values'][0]['value']
                
                data_points = []
                for value in values:
                    try:
                        # Parse date and value
                        date_str = value['dateTime']
                        value_str = value['value']
                        qualifiers = value.get('qualifiers', [])
                        
                        # Determine quality
                        quality = 'good'
                        for qualifier in qualifiers:
                            if qualifier['qualifierCode'] in ['P', 'e', 'A']:
                                quality = 'fair'
                            elif qualifier['qualifierCode'] in ['R', 'S']:
                                quality = 'poor'
                        
                        data_points.append({
                            'date': date_str[:10],  # YYYY-MM-DD
                            'value': float(value_str) if value_str != '-999999' else None,
                            'quality': quality
                        })
                    except (ValueError, KeyError) as e:
                        continue
                
                return data_points
        
        return []
    
    def _save_usgs_data(self, location_id, location_name, parameter, data_points):
        """Save USGS data in AFCA format"""
        if not data_points:
            return
        
        # Group data by year
        yearly_data = {}
        for point in data_points:
            if point['value'] is not None:
                year = point['date'][:4]
                if year not in yearly_data:
                    yearly_data[year] = []
                yearly_data[year].append(point)
        
        # Save each year's data
        for year, year_data in yearly_data.items():
            # Calculate statistics
            values = [p['value'] for p in year_data if p['value'] is not None]
            if values:
                stats = {
                    'mean': round(sum(values) / len(values), 2),
                    'min': round(min(values), 2),
                    'max': round(max(values), 2),
                    'count': len(values)
                }
                
                # Determine unit and parameter name
                if parameter == 'flow':
                    unit = 'ft³/s'
                    param_name = 'flow'
                    # Convert to daily data format
                    daily_data = self._convert_to_daily_data(year_data, 'value', 'flow_cfs')
                elif parameter == 'temperature':
                    unit = '°C'
                    param_name = 'temperature'
                    daily_data = self._convert_to_daily_data(year_data, 'value', 'temperature_c')
                elif parameter == 'stage':
                    unit = 'ft'
                    param_name = 'stage'
                    daily_data = self._convert_to_daily_data(year_data, 'value', 'stage_ft')
                else:
                    continue
                
                # Create AFCA format data
                afca_data = {
                    'location_id': location_id,
                    'location_name': location_name,
                    'year': int(year),
                    'parameter': param_name,
                    'unit': unit,
                    'data': daily_data,
                    'statistics': stats,
                    'source': 'USGS Stream Gauge Network',
                    'last_updated': datetime.now().isoformat()
                }
                
                # Save to appropriate directory
                if parameter == 'flow':
                    output_file = f"{self.output_dir}/05-flow/location-{location_id}-{year}.json"
                elif parameter == 'temperature':
                    output_file = f"{self.output_dir}/03-temperature/location-{location_id}-{year}.json"
                elif parameter == 'stage':
                    output_file = f"{self.output_dir}/06-stage/location-{location_id}-{year}.json"
                
                with open(output_file, 'w') as f:
                    json.dump(afca_data, f, indent=2)
                
                print(f"  Saved {parameter} data for {location_name} {year}: {len(daily_data)} days")
    
    def _convert_to_daily_data(self, hourly_data, value_key, output_key):
        """Convert hourly USGS data to daily averages"""
        daily_data = {}
        
        for point in hourly_data:
            date = point['date']
            if date not in daily_data:
                daily_data[date] = []
            daily_data[date].append(point)
        
        # Calculate daily averages
        daily_averages = []
        for date, day_points in daily_data.items():
            values = [p[value_key] for p in day_points if p[value_key] is not None]
            if values:
                avg_value = sum(values) / len(values)
                quality = 'good' if all(p['quality'] == 'good' for p in day_points) else 'fair'
                
                daily_averages.append({
                    'date': date,
                    output_key: round(avg_value, 2),
                    'quality': quality
                })
        
        return sorted(daily_averages, key=lambda x: x['date'])
    
    def process_epa_water_quality_data(self, location_id, location_name, csv_file):
        """Process EPA water quality data from CSV file"""
        print(f"Processing EPA water quality data for {location_name}")
        
        try:
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                
                yearly_data = {}
                for row in reader:
                    # Extract date and year
                    date_str = row.get('Date', '')
                    if not date_str:
                        continue
                    
                    try:
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                        year = str(date_obj.year)
                        
                        if year not in yearly_data:
                            yearly_data[year] = []
                        
                        # Extract water quality parameters
                        quality_data = {
                            'date': date_str,
                            'ph': self._safe_float(row.get('pH', '')),
                            'dissolved_oxygen_mg_l': self._safe_float(row.get('Dissolved_Oxygen', '')),
                            'turbidity_ntu': self._safe_float(row.get('Turbidity', '')),
                            'conductivity_us_cm': self._safe_float(row.get('Conductivity', '')),
                            'quality': 'good'  # Default quality
                        }
                        
                        yearly_data[year].append(quality_data)
                        
                    except ValueError:
                        continue
                
                # Save yearly data
                for year, year_data in yearly_data.items():
                    afca_data = {
                        'location_id': location_id,
                        'location_name': location_name,
                        'year': int(year),
                        'parameter': 'water_quality',
                        'data': year_data,
                        'source': 'EPA National Aquatic Resource Surveys',
                        'last_updated': datetime.now().isoformat()
                    }
                    
                    output_file = f"{self.output_dir}/04-quality/location-{location_id}-{year}.json"
                    with open(output_file, 'w') as f:
                        json.dump(afca_data, f, indent=2)
                    
                    print(f"  Saved water quality data for {location_name} {year}: {len(year_data)} records")
                
                return True
                
        except Exception as e:
            print(f"  Error processing EPA data: {e}")
            return False
    
    def _safe_float(self, value):
        """Safely convert string to float"""
        try:
            return float(value) if value else None
        except (ValueError, TypeError):
            return None
    
    def process_research_paper_data(self, pdf_text_file, location_mapping):
        """Process water data extracted from research papers"""
        print(f"Processing research paper data from {pdf_text_file}")
        
        try:
            with open(pdf_text_file, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Extract temperature data
            temp_data = self._extract_temperature_from_text(text)
            # Extract flow data
            flow_data = self._extract_flow_from_text(text)
            # Extract location information
            locations = self._extract_locations_from_text(text, location_mapping)
            
            # Process and save data
            for location in locations:
                location_id = location['id']
                location_name = location['name']
                
                if temp_data:
                    self._save_research_data(location_id, location_name, 'temperature', temp_data)
                if flow_data:
                    self._save_research_data(location_id, location_name, 'flow', flow_data)
            
            return True
            
        except Exception as e:
            print(f"  Error processing research paper data: {e}")
            return False
    
    def _extract_temperature_from_text(self, text):
        """Extract temperature data from research paper text"""
        temperature_patterns = [
            r'temperature[:\s]+([0-9.]+)\s*°?C',
            r'([0-9.]+)\s*°?C.*temperature',
            r'water temperature[:\s]+([0-9.]+)',
            r'stream temperature[:\s]+([0-9.]+)',
            r'([0-9.]+)\s*°C'
        ]
        
        temperatures = []
        for pattern in temperature_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    temp = float(match)
                    if 0 <= temp <= 30:  # Reasonable temperature range
                        temperatures.append(temp)
                except ValueError:
                    continue
        
        return temperatures
    
    def _extract_flow_from_text(self, text):
        """Extract flow data from research paper text"""
        flow_patterns = [
            r'flow[:\s]+([0-9,]+)\s*ft³/s',
            r'discharge[:\s]+([0-9,]+)\s*ft³/s',
            r'([0-9,]+)\s*ft³/s.*flow',
            r'streamflow[:\s]+([0-9,]+)',
            r'([0-9,]+)\s*cfs'
        ]
        
        flows = []
        for pattern in flow_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    flow = float(match.replace(',', ''))
                    if 0 <= flow <= 100000:  # Reasonable flow range
                        flows.append(flow)
                except ValueError:
                    continue
        
        return flows
    
    def _extract_locations_from_text(self, text, location_mapping):
        """Extract location information from research paper text"""
        locations = []
        for location_name, location_id in location_mapping.items():
            if re.search(location_name, text, re.IGNORECASE):
                locations.append({'id': location_id, 'name': location_name})
        
        return locations
    
    def _save_research_data(self, location_id, location_name, parameter, values):
        """Save research data in AFCA format"""
        if not values:
            return
        
        # Calculate statistics
        stats = {
            'mean': round(sum(values) / len(values), 2),
            'min': round(min(values), 2),
            'max': round(max(values), 2),
            'count': len(values)
        }
        
        # Create sample data structure (research data is typically point measurements)
        sample_data = []
        base_date = datetime(2023, 6, 1)  # Default to 2023 salmon season
        
        for i, value in enumerate(values):
            date = base_date + timedelta(days=i*7)  # Weekly intervals
            sample_data.append({
                'date': date.strftime('%Y-%m-%d'),
                f'{parameter}_c' if parameter == 'temperature' else f'{parameter}_cfs': value,
                'quality': 'good'
            })
        
        # Determine output file and data structure
        if parameter == 'temperature':
            output_file = f"{self.output_dir}/03-temperature/location-{location_id}-2023.json"
            afca_data = {
                'location_id': location_id,
                'location_name': location_name,
                'year': 2023,
                'parameter': 'temperature',
                'unit': '°C',
                'data': sample_data,
                'statistics': stats,
                'source': 'Research Paper Extraction',
                'last_updated': datetime.now().isoformat()
            }
        elif parameter == 'flow':
            output_file = f"{self.output_dir}/05-flow/location-{location_id}-2023.json"
            afca_data = {
                'location_id': location_id,
                'location_name': location_name,
                'year': 2023,
                'parameter': 'flow',
                'unit': 'ft³/s',
                'data': sample_data,
                'statistics': stats,
                'source': 'Research Paper Extraction',
                'last_updated': datetime.now().isoformat()
            }
        
        with open(output_file, 'w') as f:
            json.dump(afca_data, f, indent=2)
        
        print(f"  Saved research {parameter} data for {location_name}: {len(values)} measurements")
    
    def update_manifest(self):
        """Update manifest.json with processed data"""
        print("Updating manifest with processed data...")
        
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
                        if len(parts) >= 2:
                            try:
                                location_id = int(parts[1])
                                locations_covered.add(location_id)
                                
                                if len(parts) >= 3:
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
    print("Starting AFCA Water Data Processing Pipeline...")
    
    processor = WaterDataProcessor()
    
    # Process USGS stream gauge data for Alaska stations
    alaska_stations = [
        {"station_id": "15276000", "location_id": 410, "location_name": "Kenai River"},
        {"station_id": "15290000", "location_id": 411, "location_name": "Russian River"},
        {"station_id": "15284000", "location_id": 412, "location_name": "Moose River"}
    ]
    
    # Process recent data (2023-2024)
    for station in alaska_stations:
        for year in [2023, 2024]:
            start_date = f"{year}-06-01"
            end_date = f"{year}-09-30"
            
            processor.process_usgs_stream_gauge_data(
                station["station_id"],
                station["location_id"],
                station["location_name"],
                start_date,
                end_date
            )
    
    # Process research paper data (if available)
    location_mapping = {
        "Kenai River": 410,
        "Russian River": 411,
        "Moose River": 412,
        "Killey River": 413
    }
    
    pdf_text_dir = f"{processor.base_dir}/pdf-source-materials"
    if os.path.exists(pdf_text_dir):
        text_files = [f for f in os.listdir(pdf_text_dir) if f.endswith('.txt')]
        for text_file in text_files:
            processor.process_research_paper_data(
                f"{pdf_text_dir}/{text_file}",
                location_mapping
            )
    
    # Update manifest
    processor.update_manifest()
    
    print("\nWater data processing complete!")
    print("\nNext steps:")
    print("1. Review processed data files")
    print("2. Validate data quality and completeness")
    print("3. Test AFCA app integration")
    print("4. Add more data sources and locations")

if __name__ == "__main__":
    main()
