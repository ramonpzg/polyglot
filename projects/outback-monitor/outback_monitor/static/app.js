// Outback Monitor Dashboard JavaScript

class OutbackMonitor {
    constructor() {
        this.ws = null;
        this.charts = {};
        this.dataHistory = {
            temperature: [],
            humidity: [],
            rainfall: [],
            soilMoisture: [],
            evaporation: [],
            timestamps: []
        };
        this.maxDataPoints = 50;
        
        this.initializeCharts();
        this.bindEvents();
    }
    
    initializeCharts() {
        const chartConfig = {
            type: 'line',
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { 
                        display: false,
                        grid: { color: '#333' }
                    },
                    y: { 
                        grid: { color: '#333' },
                        ticks: { color: '#666', font: { size: 10 } }
                    }
                },
                elements: {
                    line: { borderWidth: 1, tension: 0.1 },
                    point: { radius: 0, hitRadius: 5 }
                }
            }
        };
        
        // Environment chart
        this.charts.environment = new Chart(
            document.getElementById('environmentChart'),
            {
                ...chartConfig,
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: 'Temperature (°C)',
                            data: [],
                            borderColor: '#fff',
                            backgroundColor: 'rgba(255, 255, 255, 0.1)'
                        },
                        {
                            label: 'Humidity (%)',
                            data: [],
                            borderColor: '#999',
                            backgroundColor: 'rgba(153, 153, 153, 0.1)'
                        }
                    ]
                }
            }
        );
        
        // Water chart
        this.charts.water = new Chart(
            document.getElementById('waterChart'),
            {
                ...chartConfig,
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: 'Soil Moisture (%)',
                            data: [],
                            borderColor: '#fff',
                            backgroundColor: 'rgba(255, 255, 255, 0.1)'
                        },
                        {
                            label: 'Rainfall (mm)',
                            data: [],
                            borderColor: '#ccc',
                            backgroundColor: 'rgba(204, 204, 204, 0.1)'
                        },
                        {
                            label: 'Evaporation (mm)',
                            data: [],
                            borderColor: '#666',
                            backgroundColor: 'rgba(102, 102, 102, 0.1)'
                        }
                    ]
                }
            }
        );
    }
    
    bindEvents() {
        document.getElementById('startBtn').addEventListener('click', () => this.start());
        document.getElementById('stopBtn').addEventListener('click', () => this.stop());
    }
    
    start() {
        const region = document.getElementById('regionSelect').value;
        if (!region) {
            this.setStatus('Please select a region first');
            return;
        }
        
        this.setStatus(`Connecting to ${region.toUpperCase()}...`);
        
        // Clear previous data
        this.clearData();
        
        // Connect to WebSocket
        const wsUrl = `ws://localhost:8000/ws/${region}`;
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            this.setStatus(`Monitoring ${region.toUpperCase()} - LIVE`);
            document.getElementById('startBtn').classList.add('hidden');
            document.getElementById('stopBtn').classList.remove('hidden');
            document.getElementById('dashboard').classList.remove('hidden');
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.updateData(data);
        };
        
        this.ws.onerror = () => {
            this.setStatus('Connection error - is the server running?');
        };
        
        this.ws.onclose = () => {
            if (!document.getElementById('startBtn').classList.contains('hidden')) {
                this.setStatus('Connection closed');
            }
        };
    }
    
    stop() {
        if (this.ws) {
            this.ws.close();
        }
        
        this.setStatus('Monitoring stopped');
        document.getElementById('startBtn').classList.remove('hidden');
        document.getElementById('stopBtn').classList.add('hidden');
        document.getElementById('dashboard').classList.add('hidden');
    }
    
    setStatus(message) {
        document.getElementById('status').textContent = message;
    }
    
    clearData() {
        Object.keys(this.dataHistory).forEach(key => {
            this.dataHistory[key] = [];
        });
    }
    
    updateData(data) {
        // Update metrics display
        document.getElementById('temperature').textContent = `${data.temperature}°C`;
        document.getElementById('humidity').textContent = `${data.humidity}%`;
        document.getElementById('rainfall').textContent = `${data.rainfall}mm`;
        document.getElementById('soilMoisture').textContent = `${data.soil_moisture}%`;
        document.getElementById('evaporation').textContent = `${data.evaporation}mm`;
        
        // Add to history
        const timestamp = new Date(data.timestamp).toLocaleTimeString();
        this.dataHistory.timestamps.push(timestamp);
        this.dataHistory.temperature.push(data.temperature);
        this.dataHistory.humidity.push(data.humidity);
        this.dataHistory.rainfall.push(data.rainfall);
        this.dataHistory.soilMoisture.push(data.soil_moisture);
        this.dataHistory.evaporation.push(data.evaporation);
        
        // Keep only recent data
        Object.keys(this.dataHistory).forEach(key => {
            if (this.dataHistory[key].length > this.maxDataPoints) {
                this.dataHistory[key].shift();
            }
        });
        
        // Update charts
        this.updateCharts();
    }
    
    updateCharts() {
        // Environment chart
        this.charts.environment.data.labels = this.dataHistory.timestamps;
        this.charts.environment.data.datasets[0].data = this.dataHistory.temperature;
        this.charts.environment.data.datasets[1].data = this.dataHistory.humidity;
        this.charts.environment.update('none');
        
        // Water chart
        this.charts.water.data.labels = this.dataHistory.timestamps;
        this.charts.water.data.datasets[0].data = this.dataHistory.soilMoisture;
        this.charts.water.data.datasets[1].data = this.dataHistory.rainfall;
        this.charts.water.data.datasets[2].data = this.dataHistory.evaporation;
        this.charts.water.update('none');
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    new OutbackMonitor();
});
