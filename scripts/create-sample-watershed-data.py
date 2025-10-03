#!/usr/bin/env python3
"""
AFCA Watershed Dataset Sample Data Creation Script
Creates sample water data files for testing and development
"""

import os
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

def get_working_directory():
    """Return the working directory for local storage"""
    return "."

def create_sample_temperature_data():
    """Create sample temperature data for Alaska locations"""
    print("Creating sample temperature data...")
    
    locations = [
        {"id": 410, "name": "Kenai River", "base_temp": 12.0},
        {"id": 411, "name": "Russian River", "base_temp": 11.5},
        {"id": 412, "name": "Moose River", "base_temp": 13.2},
        {"id": 413, "name": "Killey River", "base_temp": 10.8}
    ]
    
    base_dir = get_working_directory()
    
    for location in locations:
        for year in [2022, 2023, 2024]:
            # Generate daily temperature data for June-September (salmon season)
            start_date = datetime(year, 6, 1)
            end_date = datetime(year, 9, 30)
            
            daily_data = []
            current_date = start_date
            
            while current_date <= end_date:
                # Generate realistic temperature with seasonal variation
                day_of_year = current_date.timetuple().tm_yday
                seasonal_factor = 1 + 0.3 * (day_of_year - 152) / 122  # June 1 = day 152
                daily_temp = location["base_temp"] + random.uniform(-2, 3) * seasonal_factor
                
                daily_data.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "temperature_c": round(daily_temp, 1),
                    "quality": "good" if random.random() > 0.1 else "fair"
                })
                
                current_date += timedelta(days=1)
            
            # Calculate statistics
            temps = [d["temperature_c"] for d in daily_data]
            stats = {
                "mean": round(sum(temps) / len(temps), 1),
                "min": round(min(temps), 1),
                "max": round(max(temps), 1),
                "count": len(temps)
            }
            
            temp_data = {
                "location_id": location["id"],
                "location_name": location["name"],
                "year": year,
                "parameter": "temperature",
                "unit": "°C",
                "data": daily_data,
                "statistics": stats,
                "source": "USGS Stream Gauge Network",
                "last_updated": datetime.now().isoformat()
            }
            
            output_file = f"{base_dir}/data/03-temperature/location-{location['id']}-{year}.json"
            with open(output_file, "w") as f:
                json.dump(temp_data, f, indent=2)
            
            print(f"  Created temperature data: {location['name']} {year} ({len(daily_data)} days)")

def create_sample_flow_data():
    """Create sample flow data for Alaska locations"""
    print("Creating sample flow data...")
    
    locations = [
        {"id": 410, "name": "Kenai River", "base_flow": 800},
        {"id": 411, "name": "Russian River", "base_flow": 120},
        {"id": 412, "name": "Moose River", "base_flow": 450},
        {"id": 413, "name": "Killey River", "base_flow": 85}
    ]
    
    base_dir = get_working_directory()
    
    for location in locations:
        for year in [2022, 2023, 2024]:
            # Generate daily flow data for June-September
            start_date = datetime(year, 6, 1)
            end_date = datetime(year, 9, 30)
            
            daily_data = []
            current_date = start_date
            
            while current_date <= end_date:
                # Generate realistic flow with seasonal variation
                day_of_year = current_date.timetuple().tm_yday
                seasonal_factor = 1 + 0.4 * (day_of_year - 152) / 122  # June 1 = day 152
                daily_flow = location["base_flow"] + random.uniform(-200, 300) * seasonal_factor
                daily_flow = max(0, daily_flow)  # Flow can't be negative
                
                daily_data.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "flow_cfs": round(daily_flow, 0),
                    "quality": "good" if random.random() > 0.1 else "fair"
                })
                
                current_date += timedelta(days=1)
            
            # Calculate statistics
            flows = [d["flow_cfs"] for d in daily_data]
            stats = {
                "mean": round(sum(flows) / len(flows), 0),
                "min": round(min(flows), 0),
                "max": round(max(flows), 0),
                "count": len(flows)
            }
            
            flow_data = {
                "location_id": location["id"],
                "location_name": location["name"],
                "year": year,
                "parameter": "flow",
                "unit": "ft³/s",
                "data": daily_data,
                "statistics": stats,
                "source": "USGS Stream Gauge Network",
                "last_updated": datetime.now().isoformat()
            }
            
            output_file = f"{base_dir}/data/05-flow/location-{location['id']}-{year}.json"
            with open(output_file, "w") as f:
                json.dump(flow_data, f, indent=2)
            
            print(f"  Created flow data: {location['name']} {year} ({len(daily_data)} days)")

def create_sample_water_quality_data():
    """Create sample water quality data for Alaska locations"""
    print("Creating sample water quality data...")
    
    locations = [
        {"id": 410, "name": "Kenai River"},
        {"id": 411, "name": "Russian River"},
        {"id": 412, "name": "Moose River"},
        {"id": 413, "name": "Killey River"}
    ]
    
    base_dir = get_working_directory()
    
    for location in locations:
        for year in [2022, 2023, 2024]:
            # Generate weekly water quality data for June-September
            start_date = datetime(year, 6, 1)
            end_date = datetime(year, 9, 30)
            
            weekly_data = []
            current_date = start_date
            
            while current_date <= end_date:
                # Generate realistic water quality parameters
                ph = round(random.uniform(6.8, 8.2), 1)
                dissolved_oxygen = round(random.uniform(8.5, 12.0), 1)
                turbidity = round(random.uniform(0.5, 15.0), 1)
                conductivity = round(random.uniform(80, 200), 0)
                
                weekly_data.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "ph": ph,
                    "dissolved_oxygen_mg_l": dissolved_oxygen,
                    "turbidity_ntu": turbidity,
                    "conductivity_us_cm": conductivity,
                    "quality": "good" if random.random() > 0.1 else "fair"
                })
                
                current_date += timedelta(days=7)
            
            quality_data = {
                "location_id": location["id"],
                "location_name": location["name"],
                "year": year,
                "parameter": "water_quality",
                "data": weekly_data,
                "source": "ADF&G Water Quality Monitoring",
                "last_updated": datetime.now().isoformat()
            }
            
            output_file = f"{base_dir}/data/04-quality/location-{location['id']}-{year}.json"
            with open(output_file, "w") as f:
                json.dump(quality_data, f, indent=2)
            
            print(f"  Created water quality data: {location['name']} {year} ({len(weekly_data)} weeks)")

def create_sample_watershed_boundaries():
    """Create sample watershed boundary data"""
    print("Creating sample watershed boundary data...")
    
    locations = [
        {
            "id": 410,
            "name": "Kenai River",
            "drainage_area_sq_miles": 2100,
            "drainage_area_sq_km": 5440,
            "primary_tributaries": ["Russian River", "Moose River", "Killey River"]
        },
        {
            "id": 411,
            "name": "Russian River",
            "drainage_area_sq_miles": 450,
            "drainage_area_sq_km": 1165,
            "primary_tributaries": ["Russian River Falls"]
        },
        {
            "id": 412,
            "name": "Moose River",
            "drainage_area_sq_miles": 890,
            "drainage_area_sq_km": 2305,
            "primary_tributaries": ["Moose Creek", "Bear Creek"]
        },
        {
            "id": 413,
            "name": "Killey River",
            "drainage_area_sq_miles": 320,
            "drainage_area_sq_km": 829,
            "primary_tributaries": ["Killey Creek"]
        }
    ]
    
    base_dir = get_working_directory()
    
    for location in locations:
        watershed_data = {
            "location_id": location["id"],
            "location_name": location["name"],
            "watershed_name": f"{location['name']} Watershed",
            "drainage_area_sq_miles": location["drainage_area_sq_miles"],
            "drainage_area_sq_km": location["drainage_area_sq_km"],
            "primary_tributaries": location["primary_tributaries"],
            "watershed_boundary": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {
                            "name": location["name"],
                            "drainage_area_sq_miles": location["drainage_area_sq_miles"]
                        },
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [[]]  # Simplified - would contain actual coordinates
                        }
                    }
                ]
            },
            "monitoring_stations": [
                {
                    "station_id": f"KRN{location['id']:03d}",
                    "station_name": f"{location['name']} Monitoring Station",
                    "latitude": 60.4878 + random.uniform(-0.5, 0.5),
                    "longitude": -151.0583 + random.uniform(-0.5, 0.5),
                    "parameters": ["temperature", "flow", "quality"]
                }
            ],
            "data_sources": [
                {
                    "source": "USGS Watershed Boundary Dataset",
                    "url": "https://www.usgs.gov/national-hydrography/watershed-boundary-dataset",
                    "last_updated": "2024-01-01"
                }
            ],
            "last_updated": datetime.now().isoformat()
        }
        
        output_file = f"{base_dir}/data/02-watersheds/location-{location['id']}.json"
        with open(output_file, "w") as f:
            json.dump(watershed_data, f, indent=2)
        
        print(f"  Created watershed boundary: {location['name']}")

def update_manifest_with_sample_data():
    """Update manifest.json with sample data statistics"""
    print("Updating manifest with sample data...")
    
    base_dir = get_working_directory()
    manifest_path = f"{base_dir}/manifest.json"
    
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
    
    # Count files in each directory
    total_files = 0
    locations_covered = set()
    years_covered = set()
    
    for data_dir in ["02-watersheds", "03-temperature", "04-quality", "05-flow"]:
        data_path = f"{base_dir}/data/{data_dir}"
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
                        except ValueError:
                            continue
    
    # Update manifest statistics
    manifest["statistics"]["total_files"] = total_files
    manifest["statistics"]["locations_covered"] = len(locations_covered)
    manifest["statistics"]["years_covered"] = sorted(list(years_covered))
    manifest["last_updated"] = datetime.now().isoformat()
    
    # Create organized structure
    organized = {}
    for location_id in locations_covered:
        organized[str(location_id)] = {
            "watershed": f"data/02-watersheds/location-{location_id}.json",
            "temperature": {},
            "flow": {},
            "quality": {}
        }
        
        for year in years_covered:
            organized[str(location_id)]["temperature"][str(year)] = f"data/03-temperature/location-{location_id}-{year}.json"
            organized[str(location_id)]["flow"][str(year)] = f"data/05-flow/location-{location_id}-{year}.json"
            organized[str(location_id)]["quality"][str(year)] = f"data/04-quality/location-{location_id}-{year}.json"
    
    manifest["organized"] = organized
    
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    
    print(f"  Updated manifest.json with {total_files} files, {len(locations_covered)} locations, {len(years_covered)} years")

def main():
    """Main sample data creation function"""
    print("Creating sample watershed data for AFCA integration...")
    
    create_sample_temperature_data()
    create_sample_flow_data()
    create_sample_water_quality_data()
    create_sample_watershed_boundaries()
    update_manifest_with_sample_data()
    
    print("\nSample watershed data creation complete!")
    print("\nCreated sample data for:")
    print("- Temperature monitoring (daily data for June-September)")
    print("- Stream flow monitoring (daily data for June-September)")
    print("- Water quality monitoring (weekly data for June-September)")
    print("- Watershed boundaries (drainage areas and tributaries)")
    print("- Updated manifest.json with organized structure")
    
    print("\nNext steps:")
    print("1. Test data loading in AFCA app")
    print("2. Replace sample data with real USGS/EPA data")
    print("3. Add more Alaska locations")
    print("4. Initialize Git repository and push to GitHub")

if __name__ == "__main__":
    main()
