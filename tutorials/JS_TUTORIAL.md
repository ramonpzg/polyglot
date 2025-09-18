# JavaScript Tutorial: Building Real-Time Web Interfaces

*Learn JavaScript by building the Outback Monitor dashboard - a real-time agricultural monitoring system*

## Table of Contents
1. [JavaScript: The Language of Interactive Web](#javascript-the-language-of-interactive-web)
2. [Variables and Data Types](#variables-and-data-types)
3. [Functions: Your Digital Tools](#functions-your-digital-tools)
4. [Objects and Classes](#objects-and-classes)
5. [The DOM: Your Web Page Blueprint](#the-dom-your-web-page-blueprint)
6. [Asynchronous Programming](#asynchronous-programming)
7. [WebSockets: Real-Time Communication](#websockets-real-time-communication)
8. [Canvas Graphics](#canvas-graphics)
9. [Error Handling](#error-handling)
10. [Modern JavaScript Features](#modern-javascript-features)
11. [Building Our Agricultural Monitor](#building-our-agricultural-monitor)

---

## JavaScript: The Language of Interactive Web

Think of JavaScript as the **nervous system** of the web. If HTML is the skeleton and CSS is the skin, JavaScript is what makes everything move, respond, and think.

Unlike languages that run on servers or compile to machine code, JavaScript runs directly in web browsers. It's **interpreted**, meaning the browser reads and executes your code line by line.

```javascript
// Your first JavaScript - this runs immediately when the page loads
console.log("G'day from the browser!");

// JavaScript can change web pages in real-time
document.title = "Outback Monitor - Live Data";
```

**Key Insight**: JavaScript is **event-driven**. It sits quietly until something happens (user clicks, data arrives, timer fires), then springs into action.

---

## Variables and Data Types

JavaScript variables are like **storage containers** with flexible labels. Unlike strongly-typed languages, you don't declare what type of data goes in each container.

### Declaration Patterns

```javascript
// Modern sensible defaults: use const by default, let when you need to reassign
const stationName = "Broken Hill Weather Station";  // Can't be reassigned
let currentTemp = 28.5;                              // Can be reassigned
let humidity = 45;                                   // Numbers are just numbers (no int vs float)

// Avoid 'var' - it has confusing scoping rules
// var oldStyle = "don't use this";  // ❌ Avoid
```

### Data Types in Action

```javascript
// Strings - for text data
const regionName = "Queensland";
const message = `Current conditions in ${regionName}`;  // Template strings with ${} 

// Numbers - one type for all numbers
const temperature = 42.7;      // No separate int/float types
const windSpeed = 85;          // Integers are just numbers without decimals
const rainfall = 0;            // Zero is still a number

// Booleans - true/false
const isFireDangerous = temperature > 40 && humidity < 20;
const systemOnline = true;

// Arrays - ordered lists
const measurements = [28.5, 30.1, 29.8, 31.2];
const regions = ["NSW", "QLD", "VIC", "SA", "WA"];

// Objects - key-value collections (like dictionaries)
const weatherData = {
    temperature: 35.2,
    humidity: 25,
    windSpeed: 45,
    location: "Outback Station Alpha",
    timestamp: new Date()
};

// Accessing object properties
console.log(weatherData.temperature);     // Dot notation
console.log(weatherData["humidity"]);     // Bracket notation
```

**Mental Model**: Think of JavaScript objects like a **clipboard with labeled sections**. You can attach any kind of information to any label.

---

## Functions: Your Digital Tools

Functions in JavaScript are like **specialized tools** in a toolbox. Each one has a specific job and can be used repeatedly.

### Function Styles

```javascript
// Function declaration - gets "hoisted" (available anywhere in scope)
function calculateFireRisk(temp, humidity, windSpeed) {
    if (temp > 40 && humidity < 20 && windSpeed > 30) {
        return "EXTREME";
    } else if (temp > 30 && humidity < 40) {
        return "HIGH";
    } else {
        return "MODERATE";
    }
}

// Arrow functions - more concise, great for short operations
const convertToFahrenheit = (celsius) => (celsius * 9/5) + 32;

// Multi-line arrow function
const updateDisplay = (data) => {
    document.getElementById('temp').textContent = `${data.temperature}°C`;
    document.getElementById('humidity').textContent = `${data.humidity}%`;
    document.getElementById('risk').textContent = calculateFireRisk(
        data.temperature, 
        data.humidity, 
        data.windSpeed
    );
};

// Functions can be stored in variables and passed around
const processors = [
    convertToFahrenheit,
    (temp) => temp + 273.15,  // Convert to Kelvin
    (temp) => Math.round(temp)  // Round to nearest degree
];
```

### Real-World Example: Processing Weather Data

```javascript
// From our Outback Monitor project
function processWeatherUpdate(rawData) {
    const processed = {
        temperature: Math.round(rawData.temperature * 10) / 10,  // Round to 1 decimal
        humidity: Math.max(0, Math.min(100, rawData.humidity)),  // Clamp 0-100
        timestamp: new Date(rawData.timestamp),
        riskLevel: calculateFireRisk(rawData.temperature, rawData.humidity, rawData.windSpeed)
    };
    
    // Functions can call other functions
    updateDisplay(processed);
    logToHistory(processed);
    
    return processed;
}
```

---

## Objects and Classes

JavaScript objects are incredibly flexible. Think of them as **digital filing cabinets** where each drawer can hold any type of information.

### Object Patterns

```javascript
// Object literal - quick and direct
const weatherStation = {
    id: "station-001",
    location: { lat: -31.95, lng: 141.46 },
    sensors: ["temperature", "humidity", "wind"],
    
    // Methods (functions inside objects)
    getCurrentReading() {
        return {
            temperature: 32.1,
            humidity: 35,
            windSpeed: 15,
            timestamp: new Date()
        };
    },
    
    // Arrow functions behave differently in objects (be careful!)
    getLocation: () => {
        // ❌ 'this' doesn't work as expected with arrow functions in objects
        // return this.location;  // Would be undefined
        return weatherStation.location;  // ✅ Works but not ideal
    }
};

// Accessing and modifying
console.log(weatherStation.location.lat);  // -31.95
weatherStation.sensors.push("rainfall");   // Add new sensor
```

### Classes: Object Blueprints

```javascript
// Classes provide a template for creating similar objects
class OutbackMonitor {
    constructor(region, dangerLevel = 'moderate') {
        this.region = region;
        this.dangerLevel = dangerLevel;
        this.isConnected = false;
        this.dataHistory = [];
    }
    
    connect() {
        console.log(`Connecting to ${this.region.toUpperCase()} monitoring...`);
        
        // WebSocket connection (we'll cover this soon)
        this.ws = new WebSocket(`ws://localhost:8000/ws/${this.region}`);
        
        this.ws.onopen = () => {
            this.isConnected = true;
            console.log(`Connected to ${this.region}`);
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.processData(data);
        };
    }
    
    processData(data) {
        // Add to history, keep only recent data
        this.dataHistory.push(data);
        if (this.dataHistory.length > 50) {
            this.dataHistory.shift();  // Remove oldest
        }
        
        this.updateVisualization(data);
    }
    
    updateVisualization(data) {
        // Update DOM elements
        document.getElementById('temperature').textContent = `${data.temperature}°C`;
        document.getElementById('humidity').textContent = `${data.humidity}%`;
        
        // Update charts (more on this later)
        this.updateCharts();
    }
    
    updateCharts() {
        // Extract temperature data for chart
        const temperatures = this.dataHistory.map(reading => reading.temperature);
        
        // Update chart (using a charting library)
        if (this.chart) {
            this.chart.data.datasets[0].data = temperatures;
            this.chart.update('none');  // No animation for real-time
        }
    }
    
    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.isConnected = false;
        }
    }
}

// Using the class
const monitor = new OutbackMonitor('queensland', 'severe');
monitor.connect();
```

---

## The DOM: Your Web Page Blueprint

The **Document Object Model (DOM)** is like a **family tree of HTML elements**. JavaScript can read, modify, add, or remove any part of this tree in real-time.

### Finding Elements

```javascript
// Like finding specific rooms in a house
const temperatureDisplay = document.getElementById('temperature');           // By ID
const allMetrics = document.getElementsByClassName('metric-value');         // By class
const firstButton = document.querySelector('button');                      // First match
const allButtons = document.querySelectorAll('button');                   // All matches

// More specific selectors (like CSS)
const statusElements = document.querySelectorAll('.status.active');        // Multiple classes
const tempInHeader = document.querySelector('header .temperature');        // Nested elements
```

### Modifying Elements

```javascript
// Changing content and appearance
function updateWeatherDisplay(data) {
    // Change text content
    document.getElementById('temperature').textContent = `${data.temperature}°C`;
    document.getElementById('humidity').textContent = `${data.humidity}%`;
    
    // Change HTML structure
    document.getElementById('status').innerHTML = `
        <span class="icon">🔥</span>
        Fire Risk: <strong>${data.fireRisk}</strong>
    `;
    
    // Modify CSS classes
    const statusElement = document.getElementById('status');
    statusElement.classList.remove('low', 'moderate', 'high', 'extreme');
    statusElement.classList.add(data.fireRisk.toLowerCase());
    
    // Change CSS properties directly
    document.getElementById('risk-meter').style.width = `${data.riskPercentage}%`;
    
    // Modify attributes
    document.getElementById('data-chart').setAttribute('data-updated', new Date().toISOString());
}
```

### Creating New Elements

```javascript
function addNewReading(reading) {
    // Create new elements
    const readingElement = document.createElement('div');
    readingElement.classList.add('reading');
    
    // Build the content
    readingElement.innerHTML = `
        <span class="time">${new Date(reading.timestamp).toLocaleTimeString()}</span>
        <span class="temp">${reading.temperature}°C</span>
        <span class="humidity">${reading.humidity}%</span>
    `;
    
    // Add to the page
    document.getElementById('readings-list').appendChild(readingElement);
    
    // Keep only recent readings (remove old ones)
    const readings = document.querySelectorAll('.reading');
    if (readings.length > 20) {
        readings[0].remove();  // Remove oldest
    }
}
```

---

## Asynchronous Programming

JavaScript's **asynchronous** nature is like being a **restaurant server** - you don't wait for one table's order to cook before taking another table's order. You start multiple tasks and handle them as they complete.

### Callbacks: The Traditional Way

```javascript
// Old style - callback functions
function fetchWeatherData(region, callback) {
    const xhr = new XMLHttpRequest();
    xhr.open('GET', `/api/weather/${region}`);
    
    xhr.onload = function() {
        if (xhr.status === 200) {
            const data = JSON.parse(xhr.responseText);
            callback(null, data);  // Success: error=null, data=result
        } else {
            callback(new Error(`Failed to fetch data: ${xhr.status}`));
        }
    };
    
    xhr.send();
}

// Using callbacks (can get messy with multiple async operations)
fetchWeatherData('queensland', (error, data) => {
    if (error) {
        console.error('Failed to get weather:', error);
        return;
    }
    
    console.log('Weather data:', data);
    updateDisplay(data);
});
```

### Promises: A Better Way

```javascript
// Promises represent "eventual" results
function fetchWeatherData(region) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open('GET', `/api/weather/${region}`);
        
        xhr.onload = () => {
            if (xhr.status === 200) {
                const data = JSON.parse(xhr.responseText);
                resolve(data);  // Success
            } else {
                reject(new Error(`HTTP ${xhr.status}`));  // Failure
            }
        };
        
        xhr.onerror = () => reject(new Error('Network error'));
        xhr.send();
    });
}

// Using promises - much cleaner
fetchWeatherData('queensland')
    .then(data => {
        console.log('Got weather data:', data);
        updateDisplay(data);
        return fetchWeatherData('nsw');  // Chain another request
    })
    .then(nswData => {
        console.log('Got NSW data:', nswData);
        updateSecondDisplay(nswData);
    })
    .catch(error => {
        console.error('Something went wrong:', error);
        showErrorMessage(error.message);
    });
```

### Async/Await: The Modern Way

```javascript
// Modern async/await syntax - looks like synchronous code
async function updateAllRegions() {
    try {
        // These run in parallel
        const [qldData, nswData, vicData] = await Promise.all([
            fetchWeatherData('queensland'),
            fetchWeatherData('nsw'),
            fetchWeatherData('victoria')
        ]);
        
        // Update displays
        updateDisplay('qld', qldData);
        updateDisplay('nsw', nswData);
        updateDisplay('vic', vicData);
        
        console.log('All regions updated!');
        
    } catch (error) {
        console.error('Failed to update regions:', error);
        showErrorMessage('Could not fetch latest weather data');
    }
}

// Using async function
updateAllRegions();

// For sequential operations (when order matters)
async function processRegionsInOrder() {
    try {
        const regions = ['queensland', 'nsw', 'victoria'];
        
        for (const region of regions) {
            console.log(`Processing ${region}...`);
            const data = await fetchWeatherData(region);
            updateDisplay(region, data);
            
            // Wait 1 second between requests (rate limiting)
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
        
    } catch (error) {
        console.error('Processing failed:', error);
    }
}
```

---

## WebSockets: Real-Time Communication

WebSockets are like having a **dedicated phone line** between your webpage and the server. Unlike regular HTTP requests (like sending letters), WebSockets maintain a constant connection for instant two-way communication.

### Basic WebSocket Usage

```javascript
class WeatherStream {
    constructor(region) {
        this.region = region;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }
    
    connect() {
        console.log(`Connecting to ${this.region} weather stream...`);
        
        // Create WebSocket connection
        this.ws = new WebSocket(`ws://localhost:8000/ws/${this.region}`);
        
        // Connection opened
        this.ws.onopen = () => {
            console.log(`Connected to ${this.region} stream`);
            this.reconnectAttempts = 0;  // Reset counter on success
            this.updateStatus('Connected', 'success');
        };
        
        // Message received
        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleWeatherUpdate(data);
            } catch (error) {
                console.error('Failed to parse weather data:', error);
            }
        };
        
        // Connection closed
        this.ws.onclose = (event) => {
            console.log('Connection closed:', event.code, event.reason);
            this.updateStatus('Disconnected', 'error');
            
            // Attempt to reconnect if not intentional
            if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
                this.attemptReconnect();
            }
        };
        
        // Connection error
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateStatus('Connection Error', 'error');
        };
    }
    
    handleWeatherUpdate(data) {
        // Update display elements
        document.getElementById('temperature').textContent = `${data.temperature}°C`;
        document.getElementById('humidity').textContent = `${data.humidity}%`;
        document.getElementById('windSpeed').textContent = `${data.windSpeed} km/h`;
        
        // Update timestamp
        const timestamp = new Date(data.timestamp).toLocaleTimeString();
        document.getElementById('lastUpdate').textContent = `Last update: ${timestamp}`;
        
        // Update charts if they exist
        if (this.chart) {
            this.addDataPoint(data);
        }
        
        // Check for alerts
        this.checkForAlerts(data);
    }
    
    attemptReconnect() {
        this.reconnectAttempts++;
        const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000); // Exponential backoff
        
        console.log(`Attempting to reconnect in ${delay/1000}s (attempt ${this.reconnectAttempts})`);
        this.updateStatus(`Reconnecting in ${delay/1000}s...`, 'warning');
        
        setTimeout(() => {
            this.connect();
        }, delay);
    }
    
    updateStatus(message, type) {
        const statusElement = document.getElementById('connectionStatus');
        statusElement.textContent = message;
        statusElement.className = `status ${type}`;
    }
    
    checkForAlerts(data) {
        // Check for dangerous conditions
        if (data.temperature > 40 && data.humidity < 20 && data.windSpeed > 30) {
            this.showAlert('EXTREME FIRE DANGER', 'critical');
        } else if (data.temperature > 35 && data.humidity < 30) {
            this.showAlert('High Fire Risk', 'warning');
        }
    }
    
    showAlert(message, severity) {
        const alertElement = document.createElement('div');
        alertElement.classList.add('alert', severity);
        alertElement.innerHTML = `
            <span class="alert-icon">⚠️</span>
            <span class="alert-message">${message}</span>
            <button onclick="this.parentElement.remove()" class="alert-close">×</button>
        `;
        
        document.getElementById('alerts').appendChild(alertElement);
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (alertElement.parentElement) {
                alertElement.remove();
            }
        }, 10000);
    }
    
    disconnect() {
        if (this.ws) {
            this.ws.close(1000, 'User disconnected');  // Clean close
            this.ws = null;
        }
    }
}

// Usage
const weatherStream = new WeatherStream('queensland');
weatherStream.connect();

// Disconnect when page is unloaded
window.addEventListener('beforeunload', () => {
    weatherStream.disconnect();
});
```

---

## Canvas Graphics

The HTML Canvas is like a **digital drawing board**. You can draw anything on it using JavaScript - from simple shapes to complex visualizations.

### Basic Canvas Operations

```javascript
// Get canvas and drawing context
const canvas = document.getElementById('weatherChart');
const ctx = canvas.getContext('2d');

// Set canvas size
canvas.width = 400;
canvas.height = 300;

// Basic drawing functions
function drawWeatherVisualization(data) {
    // Clear the canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Set drawing styles
    ctx.fillStyle = '#333';
    ctx.strokeStyle = '#fff';
    ctx.lineWidth = 2;
    ctx.font = '14px Arial';
    
    // Draw temperature bar
    const tempHeight = (data.temperature / 50) * 200;  // Scale to canvas
    ctx.fillStyle = data.temperature > 35 ? '#ff4444' : '#44ff44';
    ctx.fillRect(50, 250 - tempHeight, 30, tempHeight);
    
    // Label the bar
    ctx.fillStyle = '#fff';
    ctx.fillText(`${data.temperature}°C`, 40, 270);
    
    // Draw humidity bar
    const humidityHeight = (data.humidity / 100) * 200;
    ctx.fillStyle = '#4444ff';
    ctx.fillRect(100, 250 - humidityHeight, 30, humidityHeight);
    ctx.fillText(`${data.humidity}%`, 95, 270);
    
    // Draw wind speed indicator (circle size)
    const windRadius = (data.windSpeed / 100) * 30;
    ctx.beginPath();
    ctx.arc(200, 150, windRadius, 0, 2 * Math.PI);
    ctx.stroke();
    ctx.fillText(`Wind: ${data.windSpeed} km/h`, 170, 200);
}
```

### Real-Time Chart Implementation

```javascript
class RealTimeChart {
    constructor(canvasId, maxDataPoints = 50) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.dataPoints = [];
        this.maxDataPoints = maxDataPoints;
        
        // Chart dimensions
        this.padding = 40;
        this.chartWidth = this.canvas.width - (this.padding * 2);
        this.chartHeight = this.canvas.height - (this.padding * 2);
    }
    
    addDataPoint(value, timestamp = new Date()) {
        this.dataPoints.push({ value, timestamp });
        
        // Keep only recent data
        if (this.dataPoints.length > this.maxDataPoints) {
            this.dataPoints.shift();
        }
        
        this.redraw();
    }
    
    redraw() {
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        if (this.dataPoints.length < 2) return;  // Need at least 2 points
        
        // Find min/max values for scaling
        const values = this.dataPoints.map(point => point.value);
        const minValue = Math.min(...values);
        const maxValue = Math.max(...values);
        const range = maxValue - minValue || 1;  // Avoid division by zero
        
        // Draw axes
        this.drawAxes(minValue, maxValue);
        
        // Draw line
        this.ctx.strokeStyle = '#00ff00';
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        
        this.dataPoints.forEach((point, index) => {
            const x = this.padding + (index / (this.maxDataPoints - 1)) * this.chartWidth;
            const y = this.padding + (1 - (point.value - minValue) / range) * this.chartHeight;
            
            if (index === 0) {
                this.ctx.moveTo(x, y);
            } else {
                this.ctx.lineTo(x, y);
            }
        });
        
        this.ctx.stroke();
        
        // Draw current value
        if (this.dataPoints.length > 0) {
            const latest = this.dataPoints[this.dataPoints.length - 1];
            this.ctx.fillStyle = '#fff';
            this.ctx.font = '16px Arial';
            this.ctx.fillText(`Current: ${latest.value}°C`, 10, 25);
        }
    }
    
    drawAxes(minValue, maxValue) {
        this.ctx.strokeStyle = '#666';
        this.ctx.lineWidth = 1;
        this.ctx.font = '12px Arial';
        this.ctx.fillStyle = '#999';
        
        // Y-axis
        this.ctx.beginPath();
        this.ctx.moveTo(this.padding, this.padding);
        this.ctx.lineTo(this.padding, this.padding + this.chartHeight);
        this.ctx.stroke();
        
        // X-axis
        this.ctx.beginPath();
        this.ctx.moveTo(this.padding, this.padding + this.chartHeight);
        this.ctx.lineTo(this.padding + this.chartWidth, this.padding + this.chartHeight);
        this.ctx.stroke();
        
        // Y-axis labels
        const steps = 5;
        for (let i = 0; i <= steps; i++) {
            const value = minValue + (maxValue - minValue) * (i / steps);
            const y = this.padding + this.chartHeight - (i / steps) * this.chartHeight;
            
            this.ctx.fillText(value.toFixed(1), 5, y + 4);
        }
    }
}

// Usage with WebSocket data
const tempChart = new RealTimeChart('temperatureChart');

// When new data arrives from WebSocket
function handleWeatherData(data) {
    tempChart.addDataPoint(data.temperature);
    // Add to other charts...
}
```

---

## Error Handling

JavaScript errors are like **flat tires** - they can stop your application dead. Good error handling is like having a **spare tire and roadside assistance**.

### Try-Catch Blocks

```javascript
// Basic error handling
function parseWeatherData(jsonString) {
    try {
        const data = JSON.parse(jsonString);
        
        // Validate the data
        if (!data.temperature || !data.humidity) {
            throw new Error('Missing required weather data fields');
        }
        
        if (data.temperature < -50 || data.temperature > 60) {
            throw new Error(`Invalid temperature reading: ${data.temperature}°C`);
        }
        
        return data;
        
    } catch (error) {
        console.error('Failed to parse weather data:', error.message);
        
        // Return default/fallback data
        return {
            temperature: 25,
            humidity: 50,
            error: true,
            errorMessage: error.message
        };
    }
}

// Error handling with async/await
async function fetchAndDisplayWeather(region) {
    try {
        const response = await fetch(`/api/weather/${region}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        const validData = parseWeatherData(JSON.stringify(data));
        
        if (validData.error) {
            showUserFriendlyError(`Data quality issue: ${validData.errorMessage}`);
        } else {
            updateWeatherDisplay(validData);
        }
        
    } catch (error) {
        console.error('Weather fetch failed:', error);
        
        if (error.name === 'TypeError') {
            showUserFriendlyError('Network connection problem. Please check your internet.');
        } else {
            showUserFriendlyError('Unable to fetch weather data. Please try again.');
        }
    }
}

function showUserFriendlyError(message) {
    const errorDiv = document.getElementById('errorDisplay');
    errorDiv.innerHTML = `
        <div class="error-message">
            <span class="error-icon">⚠️</span>
            ${message}
            <button onclick="this.parentElement.remove()">Dismiss</button>
        </div>
    `;
    errorDiv.style.display = 'block';
    
    // Auto-hide after 10 seconds
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 10000);
}
```

### Global Error Handling

```javascript
// Catch unhandled errors globally
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    
    // Log to external service (like Sentry) in production
    // logErrorToService(event.error);
    
    // Show user-friendly message
    showUserFriendlyError('Something went wrong. The page may not work correctly.');
});

// Catch unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    
    // Prevent default browser behavior (which logs to console)
    event.preventDefault();
    
    showUserFriendlyError('A background operation failed. Some features may be unavailable.');
});
```

---

## Modern JavaScript Features

JavaScript has evolved rapidly. Here are the **sensible defaults** for modern development:

### Destructuring and Spread

```javascript
// Object destructuring - extract specific properties
const weatherData = {
    temperature: 32.1,
    humidity: 45,
    windSpeed: 25,
    location: 'Darwin',
    timestamp: new Date()
};

// Extract specific properties
const { temperature, humidity, windSpeed } = weatherData;
console.log(`${temperature}°C, ${humidity}% humidity, ${windSpeed} km/h wind`);

// Rename during destructuring
const { temperature: temp, humidity: humid } = weatherData;

// Default values
const { rainfall = 0, pressure = 1013 } = weatherData;  // Defaults if not present

// Array destructuring
const coordinates = [-12.46, 130.84];  // Darwin coordinates
const [latitude, longitude] = coordinates;

// Function parameter destructuring
function displayWeather({ temperature, humidity, location, windSpeed = 0 }) {
    return `${location}: ${temperature}°C, ${humidity}% humidity, ${windSpeed} km/h wind`;
}

console.log(displayWeather(weatherData));

// Spread operator - expand arrays/objects
const baseReading = { temperature: 25, humidity: 60 };
const fullReading = { 
    ...baseReading,           // Spread base properties
    windSpeed: 15,           // Add new property
    timestamp: new Date()    // Add another property
};

// Array spreading
const regions = ['QLD', 'NSW'];
const allRegions = [...regions, 'VIC', 'SA', 'WA'];  // ['QLD', 'NSW', 'VIC', 'SA', 'WA']
```

### Template Literals and Tagged Templates

```javascript
// Template literals with expressions
const region = 'Queensland';
const temp = 38.5;
const status = temp > 35 ? 'HOT' : 'WARM';

const message = `Weather in ${region}: ${temp}°C - Status: ${status}
Risk Level: ${temp > 40 ? 'EXTREME' : 'MODERATE'}
Updated: ${new Date().toLocaleString()}`;

// Multi-line strings are easy
const htmlTemplate = `
    <div class="weather-card">
        <h3>${region}</h3>
        <div class="temperature">${temp}°C</div>
        <div class="status ${status.toLowerCase()}">${status}</div>
    </div>
`;

// Tagged template literals (advanced)
function weatherAlert(strings, ...values) {
    console.log('Template parts:', strings);  // ["Temperature: ", "°C in ", ""]
    console.log('Values:', values);           // [38.5, "Queensland"]
    
    // Custom processing
    return strings.reduce((result, string, i) => {
        const value = values[i] || '';
        const processedValue = typeof value === 'number' ? value.toFixed(1) : value;
        return result + string + processedValue;
    }, '');
}

const alertMessage = weatherAlert`Temperature: ${temp}°C in ${region}`;
```

### Maps, Sets, and Modern Iteration

```javascript
// Map - like objects but with any key type
const stationData = new Map();
stationData.set('station-001', { temp: 32, humidity: 45 });
stationData.set('station-002', { temp: 28, humidity: 60 });
stationData.set(42, { temp: 35, humidity: 30 });  // Number as key

console.log(stationData.get('station-001'));  // { temp: 32, humidity: 45 }

// Iterate over Map
for (const [stationId, data] of stationData) {
    console.log(`${stationId}: ${data.temp}°C`);
}

// Set - unique values only
const alertedRegions = new Set();
alertedRegions.add('Queensland');
alertedRegions.add('NSW');
alertedRegions.add('Queensland');  // Won't add duplicate

console.log(alertedRegions.size);  // 2
console.log(alertedRegions.has('Queensland'));  // true

// Modern array methods
const temperatures = [32.1, 28.5, 35.2, 29.8, 33.4];

// Filter, map, reduce
const hotDays = temperatures.filter(temp => temp > 30);
const fahrenheit = temperatures.map(temp => temp * 9/5 + 32);
const average = temperatures.reduce((sum, temp) => sum + temp, 0) / temperatures.length;

// Find methods
const firstHotDay = temperatures.find(temp => temp > 30);
const hotDayIndex = temperatures.findIndex(temp => temp > 30);

// Check conditions
const allHot = temperatures.every(temp => temp > 25);  // Are all temperatures > 25?
const anyExtreme = temperatures.some(temp => temp > 40);  // Any temperature > 40?
```

---

## Building Our Agricultural Monitor

Let's put it all together by building the core functionality of our Outback Monitor:

```javascript
class OutbackMonitor {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.ws = null;
        this.charts = {};
        this.dataHistory = {
            temperature: [],
            humidity: [],
            rainfall: [],
            timestamps: []
        };
        this.maxDataPoints = 50;
        
        this.initializeUI();
        this.initializeCharts();
    }
    
    initializeUI() {
        this.container.innerHTML = `
            <div class="monitor-header">
                <h2>🌾 Outback Monitor</h2>
                <div class="controls">
                    <select id="regionSelect">
                        <option value="">Select Region</option>
                        <option value="queensland">Queensland</option>
                        <option value="nsw">New South Wales</option>
                        <option value="victoria">Victoria</option>
                    </select>
                    <button id="connectBtn">Connect</button>
                    <button id="disconnectBtn" style="display: none;">Disconnect</button>
                </div>
                <div id="status" class="status">Select a region to begin</div>
            </div>
            
            <div id="dashboard" style="display: none;">
                <div class="metrics-grid">
                    <div class="metric">
                        <span class="label">Temperature</span>
                        <span id="temperature" class="value">--°C</span>
                    </div>
                    <div class="metric">
                        <span class="label">Humidity</span>
                        <span id="humidity" class="value">--%</span>
                    </div>
                    <div class="metric">
                        <span class="label">Rainfall</span>
                        <span id="rainfall" class="value">--mm</span>
                    </div>
                </div>
                
                <div class="chart-container">
                    <canvas id="environmentChart" width="600" height="300"></canvas>
                </div>
            </div>
        `;
        
        this.bindEvents();
    }
    
    bindEvents() {
        document.getElementById('connectBtn').addEventListener('click', () => {
            const region = document.getElementById('regionSelect').value;
            if (region) {
                this.connect(region);
            } else {
                this.updateStatus('Please select a region first', 'error');
            }
        });
        
        document.getElementById('disconnectBtn').addEventListener('click', () => {
            this.disconnect();
        });
    }
    
    async connect(region) {
        try {
            this.updateStatus('Connecting...', 'info');
            
            const wsUrl = `ws://localhost:8000/ws/${region}`;
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                this.updateStatus(`Connected to ${region.toUpperCase()}`, 'success');
                this.toggleControls(true);
                document.getElementById('dashboard').style.display = 'block';
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleDataUpdate(data);
                } catch (error) {
                    console.error('Failed to parse data:', error);
                }
            };
            
            this.ws.onclose = (event) => {
                this.updateStatus('Connection closed', 'error');
                this.toggleControls(false);
                
                if (event.code !== 1000) {  // Not a clean close
                    setTimeout(() => this.connect(region), 3000);  // Auto-reconnect
                }
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateStatus('Connection failed', 'error');
            };
            
        } catch (error) {
            console.error('Failed to connect:', error);
            this.updateStatus('Failed to connect', 'error');
        }
    }
    
    disconnect() {
        if (this.ws) {
            this.ws.close(1000);  // Clean close
            this.ws = null;
        }
        
        this.toggleControls(false);
        document.getElementById('dashboard').style.display = 'none';
        this.updateStatus('Disconnected', 'info');
    }
    
    handleDataUpdate(data) {
        // Update display values
        document.getElementById('temperature').textContent = `${data.temperature}°C`;
        document.getElementById('humidity').textContent = `${data.humidity}%`;
        document.getElementById('rainfall').textContent = `${data.rainfall}mm`;
        
        // Add to history
        const timestamp = new Date(data.timestamp).toLocaleTimeString();
        this.dataHistory.timestamps.push(timestamp);
        this.dataHistory.temperature.push(data.temperature);
        this.dataHistory.humidity.push(data.humidity);
        this.dataHistory.rainfall.push(data.rainfall);
        
        // Keep only recent data
        Object.keys(this.dataHistory).forEach(key => {
            if (this.dataHistory[key].length > this.maxDataPoints) {
                this.dataHistory[key].shift();
            }
        });
        
        // Update charts
        this.updateCharts();
        
        // Check for alerts
        this.checkAlerts(data);
    }
    
    initializeCharts() {
        const canvas = document.getElementById('environmentChart');
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        
        // Store chart context for updates
        this.chartContext = {
            canvas,
            ctx,
            width: canvas.width,
            height: canvas.height
        };
    }
    
    updateCharts() {
        if (!this.chartContext || this.dataHistory.temperature.length < 2) return;
        
        const { ctx, width, height } = this.chartContext;
        const padding = 40;
        const chartWidth = width - padding * 2;
        const chartHeight = height - padding * 2;
        
        // Clear canvas
        ctx.clearRect(0, 0, width, height);
        
        // Draw temperature line
        if (this.dataHistory.temperature.length > 0) {
            const temps = this.dataHistory.temperature;
            const minTemp = Math.min(...temps) - 2;
            const maxTemp = Math.max(...temps) + 2;
            const tempRange = maxTemp - minTemp || 1;
            
            // Draw axes
            ctx.strokeStyle = '#666';
            ctx.lineWidth = 1;
            
            // Y-axis
            ctx.beginPath();
            ctx.moveTo(padding, padding);
            ctx.lineTo(padding, padding + chartHeight);
            ctx.stroke();
            
            // X-axis
            ctx.beginPath();
            ctx.moveTo(padding, padding + chartHeight);
            ctx.lineTo(padding + chartWidth, padding + chartHeight);
            ctx.stroke();
            
            // Draw temperature line
            ctx.strokeStyle = '#ff6b6b';
            ctx.lineWidth = 2;
            ctx.beginPath();
            
            temps.forEach((temp, index) => {
                const x = padding + (index / (this.maxDataPoints - 1)) * chartWidth;
                const y = padding + (1 - (temp - minTemp) / tempRange) * chartHeight;
                
                if (index === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            });
            
            ctx.stroke();
            
            // Labels
            ctx.fillStyle = '#333';
            ctx.font = '12px Arial';
            ctx.fillText('Temperature (°C)', 10, 20);
            ctx.fillText(`${minTemp.toFixed(1)}°`, 5, padding + chartHeight);
            ctx.fillText(`${maxTemp.toFixed(1)}°`, 5, padding + 10);
        }
    }
    
    checkAlerts(data) {
        const { temperature, humidity, windSpeed = 0 } = data;
        
        // Fire danger calculation
        if (temperature > 35 && humidity < 30 && windSpeed > 20) {
            this.showAlert('High fire danger conditions detected!', 'warning');
        }
        
        // Extreme temperature
        if (temperature > 45) {
            this.showAlert('Extreme temperature detected!', 'critical');
        }
    }
    
    showAlert(message, severity) {
        // Create alert element
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert ${severity}`;
        alertDiv.innerHTML = `
            <span class="alert-icon">${severity === 'critical' ? '🚨' : '⚠️'}</span>
            <span class="alert-message">${message}</span>
            <button onclick="this.parentElement.remove()" class="alert-close">×</button>
        `;
        
        // Add to page (create alerts container if needed)
        let alertsContainer = document.getElementById('alerts');
        if (!alertsContainer) {
            alertsContainer = document.createElement('div');
            alertsContainer.id = 'alerts';
            alertsContainer.className = 'alerts-container';
            this.container.appendChild(alertsContainer);
        }
        
        alertsContainer.appendChild(alertDiv);
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (alertDiv.parentElement) {
                alertDiv.remove();
            }
        }, 10000);
    }
    
    updateStatus(message, type = 'info') {
        const statusElement = document.getElementById('status');
        statusElement.textContent = message;
        statusElement.className = `status ${type}`;
    }
    
    toggleControls(connected) {
        document.getElementById('connectBtn').style.display = connected ? 'none' : 'inline-block';
        document.getElementById('disconnectBtn').style.display = connected ? 'inline-block' : 'none';
        document.getElementById('regionSelect').disabled = connected;
    }
}

// Initialize when the page loads
document.addEventListener('DOMContentLoaded', () => {
    const monitor = new OutbackMonitor('monitor-container');
    
    // Make it available globally for debugging
    window.outbackMonitor = monitor;
    
    console.log('Outback Monitor initialized! 🌾');
});

// Handle page unload
window.addEventListener('beforeunload', () => {
    if (window.outbackMonitor) {
        window.outbackMonitor.disconnect();
    }
});
```

---

## Key JavaScript Concepts Summary

**Variables & Types:**
- Use `const` by default, `let` when reassigning needed
- Objects and arrays are mutable even when declared with `const`
- JavaScript has dynamic typing - variables can hold any type

**Functions:**
- Arrow functions for short operations: `const add = (a, b) => a + b`
- Regular functions for methods and when you need `this` context
- Functions are first-class values - can be passed around like data

**Async Programming:**
- Use `async/await` for cleaner asynchronous code
- `Promise.all()` for parallel operations
- WebSockets for real-time bidirectional communication

**DOM Manipulation:**
- `querySelector()` and `getElementById()` to find elements
- Modify `.textContent`, `.innerHTML`, `.classList`, and `.style`
- Event listeners respond to user interactions

**Modern Features:**
- Destructuring to extract object/array values cleanly
- Template literals for string interpolation
- Spread operator for copying/merging data structures

**Error Handling:**
- `try/catch` blocks for synchronous errors
- `.catch()` for promise errors
- Global error handlers for unhandled errors

**Sensible Defaults:**
- Use modern ES6+ features - they make code cleaner and less error-prone
- Prefer immutable operations where possible (spread, map, filter)
- Handle errors gracefully - show users friendly messages
- Use meaningful variable and function names
- Keep functions small and focused on one task

JavaScript is **event-driven** and **asynchronous** by nature. Think of it as a **responsive assistant** that waits for things to happen (clicks, data arriving, timers) and then reacts appropriately. Master the async patterns and DOM manipulation, and you'll be able to build rich, interactive web applications!
