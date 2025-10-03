#!/usr/bin/env python3
"""
AFCA Water Data Validation Script
Validates processed water data for quality and completeness
"""

import os
import json
from datetime import datetime
from pathlib import Path

def get_working_directory():
    """Return the working directory for local storage"""
    return "."

class WaterDataValidator:
    def __init__(self):
        self.base_dir = get_working_directory()
        self.data_dir = f"{self.base_dir}/data"
        self.validation_results = {
            "validation_date": datetime.now().isoformat(),
            "files_checked": 0,
            "files_valid": 0,
            "files_invalid": 0,
            "errors": [],
            "warnings": [],
            "statistics": {}
        }
    
    def validate_all_data_files(self):
        """Validate all water data files"""
        print("AFCA Water Data Validation")
        print("==========================")
        
        # Validate each data directory
        directories = ["02-watersheds", "03-temperature", "04-quality", "05-flow", "06-stage"]
        
        for directory in directories:
            dir_path = f"{self.data_dir}/{directory}"
            if os.path.exists(dir_path):
                self.validate_directory(directory, dir_path)
        
        # Generate validation report
        self.generate_validation_report()
    
    def validate_directory(self, directory_name, directory_path):
        """Validate all files in a directory"""
        print(f"\nValidating {directory_name} directory...")
        
        files = [f for f in os.listdir(directory_path) if f.endswith('.json')]
        
        for filename in files:
            file_path = f"{directory_path}/{filename}"
            self.validate_file(file_path, directory_name)
    
    def validate_file(self, file_path, directory_name):
        """Validate a single data file"""
        self.validation_results["files_checked"] += 1
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Basic structure validation
            if not self.validate_basic_structure(data, file_path):
                self.validation_results["files_invalid"] += 1
                return
            
            # Directory-specific validation
            if directory_name == "03-temperature":
                if not self.validate_temperature_data(data, file_path):
                    self.validation_results["files_invalid"] += 1
                    return
            elif directory_name == "05-flow":
                if not self.validate_flow_data(data, file_path):
                    self.validation_results["files_invalid"] += 1
                    return
            elif directory_name == "04-quality":
                if not self.validate_quality_data(data, file_path):
                    self.validation_results["files_invalid"] += 1
                    return
            elif directory_name == "02-watersheds":
                if not self.validate_watershed_data(data, file_path):
                    self.validation_results["files_invalid"] += 1
                    return
            
            self.validation_results["files_valid"] += 1
            
        except json.JSONDecodeError as e:
            self.validation_results["errors"].append({
                "file": file_path,
                "error": f"Invalid JSON format: {e}",
                "type": "json_error"
            })
            self.validation_results["files_invalid"] += 1
        except Exception as e:
            self.validation_results["errors"].append({
                "file": file_path,
                "error": f"Unexpected error: {e}",
                "type": "unexpected_error"
            })
            self.validation_results["files_invalid"] += 1
    
    def validate_basic_structure(self, data, file_path):
        """Validate basic data structure"""
        # Watershed files don't need year field, and have different structure
        if 'watershed' in file_path:
            required_fields = ['location_id', 'location_name', 'data_sources', 'last_updated']
        else:
            required_fields = ['location_id', 'location_name', 'year', 'parameter', 'source', 'last_updated']
        
        for field in required_fields:
            if field not in data:
                self.validation_results["errors"].append({
                    "file": file_path,
                    "error": f"Missing required field: {field}",
                    "type": "missing_field"
                })
                return False
        
        # Validate data types
        if not isinstance(data['location_id'], int):
            self.validation_results["errors"].append({
                "file": file_path,
                "error": "location_id must be an integer",
                "type": "type_error"
            })
            return False
        
        # Only validate year for non-watershed files
        if 'watershed' not in file_path and not isinstance(data['year'], int):
            self.validation_results["errors"].append({
                "file": file_path,
                "error": "year must be an integer",
                "type": "type_error"
            })
            return False
        
        return True
    
    def validate_temperature_data(self, data, file_path):
        """Validate temperature data"""
        # Check for data array
        if 'data' not in data:
            self.validation_results["errors"].append({
                "file": file_path,
                "error": "Missing data array",
                "type": "missing_data"
            })
            return False
        
        # Validate temperature values
        for i, day in enumerate(data['data']):
            if 'temperature_c' not in day:
                self.validation_results["errors"].append({
                    "file": file_path,
                    "error": f"Missing temperature_c in data[{i}]",
                    "type": "missing_field"
                })
                return False
            
            temp = day['temperature_c']
            if not isinstance(temp, (int, float)):
                self.validation_results["errors"].append({
                    "file": file_path,
                    "error": f"Invalid temperature value in data[{i}]: {temp}",
                    "type": "invalid_value"
                })
                return False
            
            # Check temperature range (Alaska streams)
            if temp < -5 or temp > 25:
                self.validation_results["warnings"].append({
                    "file": file_path,
                    "warning": f"Unusual temperature value in data[{i}]: {temp}°C",
                    "type": "unusual_value"
                })
        
        # Validate statistics
        if 'statistics' in data:
            stats = data['statistics']
            if 'mean' in stats and 'min' in stats and 'max' in stats:
                if not (stats['min'] <= stats['mean'] <= stats['max']):
                    self.validation_results["warnings"].append({
                        "file": file_path,
                        "warning": "Statistics min/mean/max relationship is inconsistent",
                        "type": "statistics_warning"
                    })
        
        return True
    
    def validate_flow_data(self, data, file_path):
        """Validate flow data"""
        # Check for data array
        if 'data' not in data:
            self.validation_results["errors"].append({
                "file": file_path,
                "error": "Missing data array",
                "type": "missing_data"
            })
            return False
        
        # Validate flow values
        for i, day in enumerate(data['data']):
            if 'flow_cfs' not in day:
                self.validation_results["errors"].append({
                    "file": file_path,
                    "error": f"Missing flow_cfs in data[{i}]",
                    "type": "missing_field"
                })
                return False
            
            flow = day['flow_cfs']
            if not isinstance(flow, (int, float)):
                self.validation_results["errors"].append({
                    "file": file_path,
                    "error": f"Invalid flow value in data[{i}]: {flow}",
                    "type": "invalid_value"
                })
                return False
            
            # Check flow range (Alaska streams)
            if flow < 0 or flow > 50000:
                self.validation_results["warnings"].append({
                    "file": file_path,
                    "warning": f"Unusual flow value in data[{i}]: {flow} ft³/s",
                    "type": "unusual_value"
                })
        
        return True
    
    def validate_quality_data(self, data, file_path):
        """Validate water quality data"""
        # Check for data array
        if 'data' not in data:
            self.validation_results["errors"].append({
                "file": file_path,
                "error": "Missing data array",
                "type": "missing_data"
            })
            return False
        
        # Validate quality parameters
        for i, day in enumerate(data['data']):
            # Check for at least one quality parameter
            quality_params = ['ph', 'dissolved_oxygen_mg_l', 'turbidity_ntu', 'conductivity_us_cm']
            has_param = any(param in day for param in quality_params)
            
            if not has_param:
                self.validation_results["errors"].append({
                    "file": file_path,
                    "error": f"No quality parameters found in data[{i}]",
                    "type": "missing_field"
                })
                return False
            
            # Validate pH range
            if 'ph' in day:
                ph = day['ph']
                if not isinstance(ph, (int, float)):
                    self.validation_results["errors"].append({
                        "file": file_path,
                        "error": f"Invalid pH value in data[{i}]: {ph}",
                        "type": "invalid_value"
                    })
                    return False
                
                if ph < 4 or ph > 10:
                    self.validation_results["warnings"].append({
                        "file": file_path,
                        "warning": f"Unusual pH value in data[{i}]: {ph}",
                        "type": "unusual_value"
                    })
        
        return True
    
    def validate_watershed_data(self, data, file_path):
        """Validate watershed boundary data"""
        # Check for required watershed fields
        required_fields = ['drainage_area_sq_miles', 'primary_tributaries']
        
        for field in required_fields:
            if field not in data:
                self.validation_results["errors"].append({
                    "file": file_path,
                    "error": f"Missing required watershed field: {field}",
                    "type": "missing_field"
                })
                return False
        
        # Validate drainage area
        if not isinstance(data['drainage_area_sq_miles'], (int, float)):
            self.validation_results["errors"].append({
                "file": file_path,
                "error": "drainage_area_sq_miles must be a number",
                "type": "type_error"
            })
            return False
        
        if data['drainage_area_sq_miles'] <= 0:
            self.validation_results["warnings"].append({
                "file": file_path,
                "warning": "drainage_area_sq_miles should be positive",
                "type": "unusual_value"
            })
        
        return True
    
    def generate_validation_report(self):
        """Generate validation report"""
        print(f"\nValidation Complete")
        print(f"==================")
        print(f"Files checked: {self.validation_results['files_checked']}")
        print(f"Files valid: {self.validation_results['files_valid']}")
        print(f"Files invalid: {self.validation_results['files_invalid']}")
        print(f"Errors: {len(self.validation_results['errors'])}")
        print(f"Warnings: {len(self.validation_results['warnings'])}")
        
        if self.validation_results['errors']:
            print(f"\nErrors:")
            for error in self.validation_results['errors']:
                print(f"  {error['file']}: {error['error']}")
        
        if self.validation_results['warnings']:
            print(f"\nWarnings:")
            for warning in self.validation_results['warnings']:
                print(f"  {warning['file']}: {warning['warning']}")
        
        # Save validation report
        report_file = f"{self.base_dir}/validation-report.json"
        with open(report_file, 'w') as f:
            json.dump(self.validation_results, f, indent=2)
        
        print(f"\nValidation report saved: {report_file}")
        
        # Calculate success rate
        if self.validation_results['files_checked'] > 0:
            success_rate = (self.validation_results['files_valid'] / self.validation_results['files_checked']) * 100
            print(f"Success rate: {success_rate:.1f}%")
            
            if success_rate >= 95:
                print("✅ Data quality is excellent")
            elif success_rate >= 85:
                print("⚠️ Data quality is good with minor issues")
            else:
                print("❌ Data quality needs improvement")

def main():
    """Main validation function"""
    validator = WaterDataValidator()
    validator.validate_all_data_files()

if __name__ == "__main__":
    main()
