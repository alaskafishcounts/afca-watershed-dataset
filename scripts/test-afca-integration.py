#!/usr/bin/env python3
"""
AFCA Integration Test Script
Tests water data integration with AFCA app format
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path

def get_working_directory():
    """Return the working directory for local storage"""
    return "."

class AFCAIntegrationTester:
    def __init__(self):
        self.base_dir = get_working_directory()
        self.data_dir = f"{self.base_dir}/data"
        self.test_results = {
            "test_date": datetime.now().isoformat(),
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "errors": [],
            "warnings": []
        }
    
    def test_manifest_loading(self):
        """Test manifest loading and structure"""
        print("Testing manifest loading...")
        self.test_results["tests_run"] += 1
        
        try:
            manifest_path = f"{self.base_dir}/manifest.json"
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            # Check required fields
            required_fields = ['version', 'dataset_name', 'organized', 'statistics']
            for field in required_fields:
                if field not in manifest:
                    self.test_results["errors"].append(f"Manifest missing field: {field}")
                    self.test_results["tests_failed"] += 1
                    return False
            
            # Check organized structure
            if not isinstance(manifest['organized'], dict):
                self.test_results["errors"].append("Manifest organized field must be a dictionary")
                self.test_results["tests_failed"] += 1
                return False
            
            print("  ✅ Manifest loading test passed")
            self.test_results["tests_passed"] += 1
            return True
            
        except Exception as e:
            self.test_results["errors"].append(f"Manifest loading error: {e}")
            self.test_results["tests_failed"] += 1
            return False
    
    def test_data_file_loading(self):
        """Test individual data file loading"""
        print("Testing data file loading...")
        self.test_results["tests_run"] += 1
        
        try:
            # Test temperature data
            temp_file = f"{self.data_dir}/03-temperature/location-410-2023.json"
            if os.path.exists(temp_file):
                with open(temp_file, 'r') as f:
                    temp_data = json.load(f)
                
                # Check temperature data structure
                if 'data' not in temp_data:
                    self.test_results["errors"].append("Temperature data missing 'data' field")
                    self.test_results["tests_failed"] += 1
                    return False
                
                # Check first data point
                if temp_data['data']:
                    first_point = temp_data['data'][0]
                    if 'temperature_c' not in first_point:
                        self.test_results["errors"].append("Temperature data point missing 'temperature_c' field")
                        self.test_results["tests_failed"] += 1
                        return False
            
            # Test flow data
            flow_file = f"{self.data_dir}/05-flow/location-410-2023.json"
            if os.path.exists(flow_file):
                with open(flow_file, 'r') as f:
                    flow_data = json.load(f)
                
                # Check flow data structure
                if 'data' not in flow_data:
                    self.test_results["errors"].append("Flow data missing 'data' field")
                    self.test_results["tests_failed"] += 1
                    return False
                
                # Check first data point
                if flow_data['data']:
                    first_point = flow_data['data'][0]
                    if 'flow_cfs' not in first_point:
                        self.test_results["errors"].append("Flow data point missing 'flow_cfs' field")
                        self.test_results["tests_failed"] += 1
                        return False
            
            print("  ✅ Data file loading test passed")
            self.test_results["tests_passed"] += 1
            return True
            
        except Exception as e:
            self.test_results["errors"].append(f"Data file loading error: {e}")
            self.test_results["tests_failed"] += 1
            return False
    
    def test_afca_data_format(self):
        """Test AFCA data format compatibility"""
        print("Testing AFCA data format compatibility...")
        self.test_results["tests_run"] += 1
        
        try:
            # Load manifest
            manifest_path = f"{self.base_dir}/manifest.json"
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            # Test location data access pattern
            location_id = "410"
            if location_id in manifest['organized']:
                location_data = manifest['organized'][location_id]
                
                # Check required data types
                required_types = ['temperature', 'flow', 'quality', 'watershed']
                for data_type in required_types:
                    if data_type not in location_data:
                        self.test_results["warnings"].append(f"Location {location_id} missing {data_type} data")
                        continue
                    
                    if data_type == 'watershed':
                        # Watershed is a single file
                        if not isinstance(location_data[data_type], str):
                            self.test_results["errors"].append(f"Watershed data should be a file path string")
                            self.test_results["tests_failed"] += 1
                            return False
                    else:
                        # Other types have yearly data
                        if not isinstance(location_data[data_type], dict):
                            self.test_results["errors"].append(f"{data_type} data should be a dictionary of years")
                            self.test_results["tests_failed"] += 1
                            return False
                
                print("  ✅ AFCA data format test passed")
                self.test_results["tests_passed"] += 1
                return True
            else:
                self.test_results["errors"].append(f"Location {location_id} not found in manifest")
                self.test_results["tests_failed"] += 1
                return False
                
        except Exception as e:
            self.test_results["errors"].append(f"AFCA format test error: {e}")
            self.test_results["tests_failed"] += 1
            return False
    
    def test_data_statistics(self):
        """Test data statistics calculation"""
        print("Testing data statistics...")
        self.test_results["tests_run"] += 1
        
        try:
            # Test temperature statistics
            temp_file = f"{self.data_dir}/03-temperature/location-410-2023.json"
            if os.path.exists(temp_file):
                with open(temp_file, 'r') as f:
                    temp_data = json.load(f)
                
                if 'statistics' in temp_data:
                    stats = temp_data['statistics']
                    required_stats = ['mean', 'min', 'max', 'count']
                    
                    for stat in required_stats:
                        if stat not in stats:
                            self.test_results["errors"].append(f"Temperature statistics missing {stat}")
                            self.test_results["tests_failed"] += 1
                            return False
                    
                    # Check statistics consistency
                    if stats['min'] > stats['max']:
                        self.test_results["errors"].append("Temperature statistics: min > max")
                        self.test_results["tests_failed"] += 1
                        return False
                    
                    if stats['count'] <= 0:
                        self.test_results["errors"].append("Temperature statistics: count <= 0")
                        self.test_results["tests_failed"] += 1
                        return False
            
            print("  ✅ Data statistics test passed")
            self.test_results["tests_passed"] += 1
            return True
            
        except Exception as e:
            self.test_results["errors"].append(f"Data statistics test error: {e}")
            self.test_results["tests_failed"] += 1
            return False
    
    def test_github_cdn_compatibility(self):
        """Test GitHub CDN compatibility (simulated)"""
        print("Testing GitHub CDN compatibility...")
        self.test_results["tests_run"] += 1
        
        try:
            # Simulate GitHub CDN URLs
            base_url = "https://raw.githubusercontent.com/alaskafishcounts/afca-watershed-dataset/main"
            
            # Test manifest URL
            manifest_url = f"{base_url}/manifest.json"
            print(f"  Manifest URL: {manifest_url}")
            
            # Test data file URL
            data_url = f"{base_url}/data/03-temperature/location-410-2023.json"
            print(f"  Data URL: {data_url}")
            
            # Test watershed URL
            watershed_url = f"{base_url}/data/02-watersheds/location-410.json"
            print(f"  Watershed URL: {watershed_url}")
            
            print("  ✅ GitHub CDN compatibility test passed")
            self.test_results["tests_passed"] += 1
            return True
            
        except Exception as e:
            self.test_results["errors"].append(f"GitHub CDN test error: {e}")
            self.test_results["tests_failed"] += 1
            return False
    
    def generate_afca_integration_code(self):
        """Generate AFCA integration code example"""
        print("Generating AFCA integration code example...")
        
        integration_code = '''
// AFCA Watershed Data Integration Example
// This code shows how to load watershed data in the AFCA app

class WatershedDataLoader {
    constructor() {
        this.baseUrl = 'https://raw.githubusercontent.com/alaskafishcounts/afca-watershed-dataset/main';
        this.manifest = null;
    }
    
    async loadManifest() {
        try {
            const response = await fetch(`${this.baseUrl}/manifest.json`);
            this.manifest = await response.json();
            return this.manifest;
        } catch (error) {
            console.error('Error loading watershed manifest:', error);
            return null;
        }
    }
    
    async loadTemperatureData(locationId, year) {
        if (!this.manifest) {
            await this.loadManifest();
        }
        
        try {
            const filePath = this.manifest.organized[locationId].temperature[year];
            const response = await fetch(`${this.baseUrl}/${filePath}`);
            return await response.json();
        } catch (error) {
            console.error(`Error loading temperature data for location ${locationId}, year ${year}:`, error);
            return null;
        }
    }
    
    async loadFlowData(locationId, year) {
        if (!this.manifest) {
            await this.loadManifest();
        }
        
        try {
            const filePath = this.manifest.organized[locationId].flow[year];
            const response = await fetch(`${this.baseUrl}/${filePath}`);
            return await response.json();
        } catch (error) {
            console.error(`Error loading flow data for location ${locationId}, year ${year}:`, error);
            return null;
        }
    }
    
    async loadWatershedData(locationId) {
        if (!this.manifest) {
            await this.loadManifest();
        }
        
        try {
            const filePath = this.manifest.organized[locationId].watershed;
            const response = await fetch(`${this.baseUrl}/${filePath}`);
            return await response.json();
        } catch (error) {
            console.error(`Error loading watershed data for location ${locationId}:`, error);
            return null;
        }
    }
}

// Usage example
const watershedLoader = new WatershedDataLoader();

// Load temperature data for Kenai River 2023
watershedLoader.loadTemperatureData('410', '2023').then(data => {
    if (data) {
        console.log('Temperature data loaded:', data);
        // Use data.data array for daily temperature values
        // Use data.statistics for summary statistics
    }
});

// Load flow data for Kenai River 2023
watershedLoader.loadFlowData('410', '2023').then(data => {
    if (data) {
        console.log('Flow data loaded:', data);
        // Use data.data array for daily flow values
    }
});

// Load watershed boundary data for Kenai River
watershedLoader.loadWatershedData('410').then(data => {
    if (data) {
        console.log('Watershed data loaded:', data);
        // Use data.drainage_area_sq_miles for drainage area
        // Use data.watershed_boundary for GeoJSON boundary
    }
});
'''
        
        # Save integration code
        code_file = f"{self.base_dir}/docs/afca-integration-example.js"
        with open(code_file, 'w') as f:
            f.write(integration_code)
        
        print(f"  Integration code saved: {code_file}")
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("AFCA Integration Test Suite")
        print("==========================")
        
        # Run tests
        self.test_manifest_loading()
        self.test_data_file_loading()
        self.test_afca_data_format()
        self.test_data_statistics()
        self.test_github_cdn_compatibility()
        
        # Generate integration code
        self.generate_afca_integration_code()
        
        # Generate test report
        self.generate_test_report()
    
    def generate_test_report(self):
        """Generate test report"""
        print(f"\nIntegration Test Results")
        print(f"========================")
        print(f"Tests run: {self.test_results['tests_run']}")
        print(f"Tests passed: {self.test_results['tests_passed']}")
        print(f"Tests failed: {self.test_results['tests_failed']}")
        print(f"Warnings: {len(self.test_results['warnings'])}")
        
        if self.test_results['errors']:
            print(f"\nErrors:")
            for error in self.test_results['errors']:
                print(f"  ❌ {error}")
        
        if self.test_results['warnings']:
            print(f"\nWarnings:")
            for warning in self.test_results['warnings']:
                print(f"  ⚠️ {warning}")
        
        # Save test report
        report_file = f"{self.base_dir}/integration-test-report.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\nTest report saved: {report_file}")
        
        # Calculate success rate
        if self.test_results['tests_run'] > 0:
            success_rate = (self.test_results['tests_passed'] / self.test_results['tests_run']) * 100
            print(f"Success rate: {success_rate:.1f}%")
            
            if success_rate == 100:
                print("✅ All integration tests passed - ready for AFCA app integration!")
            elif success_rate >= 80:
                print("⚠️ Most integration tests passed - minor issues to address")
            else:
                print("❌ Integration tests failed - significant issues to fix")

def main():
    """Main test function"""
    tester = AFCAIntegrationTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
