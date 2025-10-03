
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
