#!/usr/bin/env python3
"""
AFCA Watershed Data Extraction Script
Extracts water data from research papers and organizes it for AFCA integration
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path

def get_working_directory():
    """Return the working directory for local storage"""
    return "afca-watershed-dataset"

def extract_temperature_data_from_text(text):
    """Extract temperature data from research paper text"""
    temperature_patterns = [
        r'temperature[:\s]+([0-9.]+)\s*°?C',
        r'([0-9.]+)\s*°?C.*temperature',
        r'water temperature[:\s]+([0-9.]+)',
        r'stream temperature[:\s]+([0-9.]+)'
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

def extract_flow_data_from_text(text):
    """Extract flow data from research paper text"""
    flow_patterns = [
        r'flow[:\s]+([0-9,]+)\s*ft³/s',
        r'discharge[:\s]+([0-9,]+)\s*ft³/s',
        r'([0-9,]+)\s*ft³/s.*flow',
        r'streamflow[:\s]+([0-9,]+)'
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

def extract_location_data_from_text(text):
    """Extract location information from research paper text"""
    location_patterns = [
        r'Kenai River',
        r'Russian River',
        r'Moose River',
        r'Killey River',
        r'Soldotna',
        r'Cooper Landing'
    ]
    
    locations = []
    for pattern in location_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            locations.append(pattern)
    
    return locations

def create_watershed_data_entry(location, temperatures, flows, source_info):
    """Create a structured data entry for watershed data"""
    return {
        "location_name": location,
        "location_id": None,  # Will be mapped later
        "data_type": "watershed_research",
        "source": source_info,
        "extracted_data": {
            "temperatures": {
                "values": temperatures,
                "statistics": {
                    "mean": sum(temperatures) / len(temperatures) if temperatures else None,
                    "min": min(temperatures) if temperatures else None,
                    "max": max(temperatures) if temperatures else None,
                    "count": len(temperatures)
                }
            },
            "flows": {
                "values": flows,
                "statistics": {
                    "mean": sum(flows) / len(flows) if flows else None,
                    "min": min(flows) if flows else None,
                    "max": max(flows) if flows else None,
                    "count": len(flows)
                }
            }
        },
        "extraction_date": datetime.now().isoformat(),
        "quality_notes": "Data extracted from research paper text"
    }

def process_pdf_text_file(file_path):
    """Process a text file extracted from PDF"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Extract data
        temperatures = extract_temperature_data_from_text(text)
        flows = extract_flow_data_from_text(text)
        locations = extract_location_data_from_text(text)
        
        # Create data entries
        entries = []
        for location in locations:
            entry = create_watershed_data_entry(
                location, temperatures, flows, 
                {"file": file_path, "type": "research_paper"}
            )
            entries.append(entry)
        
        return entries
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []

def save_extracted_data(entries, output_file):
    """Save extracted data to JSON file"""
    base_dir = get_working_directory()
    output_path = f"{base_dir}/data/02-watersheds/{output_file}"
    
    with open(output_path, 'w') as f:
        json.dump(entries, f, indent=2)
    
    print(f"Saved {len(entries)} entries to {output_path}")

def map_locations_to_afca_ids(entries):
    """Map location names to AFCA location IDs"""
    location_mapping = {
        "Kenai River": 410,
        "Russian River": 411,
        "Moose River": 412,
        "Killey River": 413,
        "Soldotna": 410,
        "Cooper Landing": 414
    }
    
    for entry in entries:
        location_name = entry["location_name"]
        if location_name in location_mapping:
            entry["location_id"] = location_mapping[location_name]
    
    return entries

def main():
    """Main extraction function"""
    print("Extracting watershed data from research papers...")
    
    base_dir = get_working_directory()
    pdf_dir = f"{base_dir}/pdf-source-materials"
    
    if not os.path.exists(pdf_dir):
        print(f"PDF directory not found: {pdf_dir}")
        return
    
    # Look for text files (extracted from PDFs)
    text_files = [f for f in os.listdir(pdf_dir) if f.endswith('.txt')]
    
    if not text_files:
        print("No text files found. Please extract text from PDFs first.")
        print("You can use tools like pdftotext or online PDF text extractors.")
        return
    
    all_entries = []
    
    for text_file in text_files:
        file_path = f"{pdf_dir}/{text_file}"
        print(f"Processing: {text_file}")
        
        entries = process_pdf_text_file(file_path)
        all_entries.extend(entries)
    
    # Map locations to AFCA IDs
    all_entries = map_locations_to_afca_ids(all_entries)
    
    # Save extracted data
    if all_entries:
        save_extracted_data(all_entries, "extracted-research-data.json")
        print(f"\nExtraction complete! Found data for {len(set(e['location_name'] for e in all_entries))} locations")
    else:
        print("No data extracted. Check PDF text extraction.")

if __name__ == "__main__":
    main()
