<template>
  <div class="outback-demo">
    <div class="demo-header">
      <h3>🌾 Outback Monitor</h3>
      <div class="status" :class="{ 'connected': isConnected }">
        {{ status }}
      </div>
    </div>
    
    <div class="controls">
      <select v-model="selectedRegion" :disabled="isConnected">
        <option value="">Select Region</option>
        <option value="queensland">Queensland</option>
        <option value="nsw">New South Wales</option>
        <option value="victoria">Victoria</option>
        <option value="sa">South Australia</option>
        <option value="wa">Western Australia</option>
      </select>
      <button @click="toggle" :disabled="!selectedRegion">
        {{ isConnected ? 'STOP' : 'START' }}
      </button>
    </div>
    
    <div v-if="currentData" class="metrics">
      <div class="metric">
        <div class="label">Temperature</div>
        <div class="value">{{ currentData.temperature }}°C</div>
      </div>
      <div class="metric">
        <div class="label">Humidity</div>
        <div class="value">{{ currentData.humidity }}%</div>
      </div>
      <div class="metric">
        <div class="label">Soil Moisture</div>
        <div class="value">{{ currentData.soil_moisture }}%</div>
      </div>
      <div class="metric">
        <div class="label">Rainfall</div>
        <div class="value">{{ currentData.rainfall }}mm</div>
      </div>
    </div>
    
    <div v-if="isConnected" class="mini-chart">
      <canvas ref="chartCanvas" width="400" height="100"></canvas>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'

const selectedRegion = ref('')
const isConnected = ref(false)
const status = ref('Select a region to begin')
const currentData = ref(null)
const ws = ref(null)
const chartCanvas = ref(null)
const dataHistory = ref([])
const maxPoints = 20

let chart = null

const toggle = () => {
  if (isConnected.value) {
    disconnect()
  } else {
    connect()
  }
}

const connect = async () => {
  if (!selectedRegion.value) return
  
  status.value = 'Connecting...'
  
  try {
    ws.value = new WebSocket(`ws://localhost:8000/ws/${selectedRegion.value}`)
    
    ws.value.onopen = () => {
      isConnected.value = true
      status.value = `Monitoring ${selectedRegion.value.toUpperCase()}`
      dataHistory.value = []
      nextTick(() => initChart())
    }
    
    ws.value.onmessage = (event) => {
      const data = JSON.parse(event.data)
      currentData.value = data
      updateChart(data)
    }
    
    ws.value.onerror = () => {
      status.value = 'Connection failed'
      isConnected.value = false
    }
    
    ws.value.onclose = () => {
      if (isConnected.value) {
        status.value = 'Connection lost'
        isConnected.value = false
      }
    }
  } catch (error) {
    status.value = 'Failed to connect'
  }
}

const disconnect = () => {
  if (ws.value) {
    ws.value.close()
  }
  isConnected.value = false
  status.value = 'Disconnected'
  currentData.value = null
}

const initChart = () => {
  if (!chartCanvas.value) return
  
  const ctx = chartCanvas.value.getContext('2d')
  chart = {
    ctx,
    width: chartCanvas.value.width,
    height: chartCanvas.value.height
  }
  
  // Clear canvas
  ctx.fillStyle = '#000'
  ctx.fillRect(0, 0, chart.width, chart.height)
}

const updateChart = (data) => {
  if (!chart) return
  
  dataHistory.value.push(data.temperature)
  if (dataHistory.value.length > maxPoints) {
    dataHistory.value.shift()
  }
  
  const { ctx, width, height } = chart
  
  // Clear canvas
  ctx.fillStyle = '#000'
  ctx.fillRect(0, 0, width, height)
  
  // Draw temperature line
  if (dataHistory.value.length > 1) {
    ctx.strokeStyle = '#fff'
    ctx.lineWidth = 1
    ctx.beginPath()
    
    const stepX = width / (maxPoints - 1)
    const minTemp = 15
    const maxTemp = 40
    
    dataHistory.value.forEach((temp, i) => {
      const x = i * stepX
      const y = height - ((temp - minTemp) / (maxTemp - minTemp)) * height
      
      if (i === 0) {
        ctx.moveTo(x, y)
      } else {
        ctx.lineTo(x, y)
      }
    })
    
    ctx.stroke()
  }
  
  // Draw labels
  ctx.fillStyle = '#666'
  ctx.font = '10px monospace'
  ctx.fillText('Temperature (°C)', 5, 15)
}

onUnmounted(() => {
  disconnect()
})
</script>

<style scoped>
.outback-demo {
  background: #000;
  color: #fff;
  font-family: 'Monaco', 'Menlo', monospace;
  padding: 20px;
  border: 1px solid #333;
  font-size: 12px;
  max-width: 500px;
  margin: 0 auto;
}

.demo-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.demo-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: normal;
}

.status {
  font-size: 10px;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.status.connected {
  color: #fff;
}

.controls {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
  justify-content: center;
}

select, button {
  background: #000;
  color: #fff;
  border: 1px solid #333;
  padding: 5px 10px;
  font-family: inherit;
  font-size: 11px;
}

button:hover:not(:disabled) {
  border-color: #666;
}

button:disabled {
  opacity: 0.5;
}

.metrics {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-bottom: 15px;
}

.metric {
  text-align: center;
  border: 1px solid #333;
  padding: 8px;
}

.metric .label {
  font-size: 9px;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.metric .value {
  font-size: 14px;
  margin-top: 3px;
}

.mini-chart {
  border: 1px solid #333;
  padding: 10px;
  text-align: center;
}

.mini-chart canvas {
  background: #000;
  border: 1px solid #333;
}
</style>
