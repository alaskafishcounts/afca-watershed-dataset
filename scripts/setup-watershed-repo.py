#!/usr/bin/env python3
"""
AFCA Watershed Dataset Repository Setup Script
Creates the initial repository structure and downloads source materials
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path

def get_working_directory():
    """Return the working directory for local storage"""
    return "."

def create_directory_structure():
    """Create the complete directory structure for the watershed dataset"""
    base_dir = get_working_directory()
    
    directories = [
        f"{base_dir}/data/01-master",
        f"{base_dir}/data/02-watersheds", 
        f"{base_dir}/data/03-temperature",
        f"{base_dir}/data/04-quality",
        f"{base_dir}/data/05-flow",
        f"{base_dir}/scripts",
        f"{base_dir}/docs",
        f"{base_dir}/pdf-source-materials"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

def download_research_papers():
    """Download key research papers for watershed data"""
    papers = [
        {
            "title": "Canadian Journal of Fisheries and Aquatic Sciences 2016",
            "url": "https://cdnsciencepub.com/doi/full/10.1139/cjfas-2016-0076",
            "filename": "cjfas-2016-0076-watershed-research.pdf"
        }
    ]
    
    pdf_dir = f"{get_working_directory()}/pdf-source-materials"
    
    for paper in papers:
        try:
            print(f"Downloading: {paper['title']}")
            # Note: This would need to be adapted for actual PDF download
            # Many academic papers require authentication or have access restrictions
            print(f"  URL: {paper['url']}")
            print(f"  Target: {pdf_dir}/{paper['filename']}")
            print("  Note: Manual download may be required due to access restrictions")
        except Exception as e:
            print(f"  Error downloading {paper['title']}: {e}")

def create_sample_data_files():
    """Create sample data files for testing"""
    base_dir = get_working_directory()
    
    # Sample temperature data
    temp_data = {
        "location_id": 410,
        "location_name": "Kenai River",
        "year": 2023,
        "parameter": "temperature",
        "unit": "°C",
        "data": [
            {"date": "2023-06-01", "value": 12.5, "quality": "good"},
            {"date": "2023-06-02", "value": 13.2, "quality": "good"},
            {"date": "2023-06-03", "value": 14.1, "quality": "good"}
        ],
        "statistics": {
            "mean": 13.27,
            "min": 12.5,
            "max": 14.1,
            "count": 3
        },
        "source": "USGS Stream Gauge Network",
        "last_updated": datetime.now().isoformat()
    }
    
    with open(f"{base_dir}/data/03-temperature/location-410-2023.json", "w") as f:
        json.dump(temp_data, f, indent=2)
    
    print("Created sample temperature data file")

def update_manifest():
    """Update the manifest.json with current statistics"""
    manifest_path = f"{get_working_directory()}/manifest.json"
    
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
    
    # Count files in each directory
    base_dir = get_working_directory()
    total_files = 0
    
    for data_dir in ["02-watersheds", "03-temperature", "04-quality", "05-flow"]:
        data_path = f"{base_dir}/data/{data_dir}"
        if os.path.exists(data_path):
            files = [f for f in os.listdir(data_path) if f.endswith('.json')]
            total_files += len(files)
    
    manifest["statistics"]["total_files"] = total_files
    manifest["last_updated"] = datetime.now().isoformat()
    
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    
    print(f"Updated manifest.json with {total_files} total files")

def main():
    """Main setup function"""
    print("Setting up AFCA Watershed Dataset Repository...")
    
    create_directory_structure()
    download_research_papers()
    create_sample_data_files()
    update_manifest()
    
    print("\nRepository setup complete!")
    print(f"Working directory: {get_working_directory()}")
    print("\nNext steps:")
    print("1. Download research papers manually from pdf-source-materials/")
    print("2. Extract water data from PDFs using analysis scripts")
    print("3. Organize data by location and year")
    print("4. Update manifest.json with actual file counts")
    print("5. Initialize Git repository and push to GitHub")

if __name__ == "__main__":
    main()
