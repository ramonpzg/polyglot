<template>
  <div class="bush-ears-demo">
    <div class="demo-header">
      <h3>🦘 Bush Ears</h3>
      <div class="status" :class="{ 'monitoring': isMonitoring }">
        {{ status }}
      </div>
    </div>
    
    <div class="controls">
      <select v-model="selectedScenario" :disabled="isMonitoring">
        <option value="dawn_chorus">Dawn Chorus</option>
        <option value="urban_park">Urban Park</option>
        <option value="outback_night">Outback Night</option>
        <option value="endangered_habitat">Endangered Habitat</option>
      </select>
      <button @click="toggle" :disabled="!selectedScenario">
        {{ isMonitoring ? 'STOP' : 'START' }}
      </button>
      <button @click="reset" :disabled="isMonitoring">RESET</button>
    </div>
    
    <div class="main-area">
      <div class="detections">
        <h4>Live Detections</h4>
        <div class="detection-list">
          <div v-for="detection in recentDetections" 
               :key="detection.id" 
               class="detection"
               :class="{ 'new': detection.isNew }">
            <span class="species-icon">{{ getSpeciesIcon(detection.species) }}</span>
            <div class="detection-info">
              <strong>{{ detection.species }}</strong>
              <div class="detection-time">{{ detection.time }}s</div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="metrics">
        <div class="metric">
          <div class="label">Biodiversity</div>
          <div class="value">{{ biodiversity.toFixed(2) }}</div>
        </div>
        <div class="metric">
          <div class="label">Conservation</div>
          <div class="value">{{ conservation.toFixed(2) }}</div>
        </div>
        <div class="metric">
          <div class="label">Species</div>
          <div class="value">{{ speciesCount }}</div>
        </div>
        <div class="metric">
          <div class="label">Detections</div>
          <div class="value">{{ totalDetections }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const selectedScenario = ref('dawn_chorus')
const isMonitoring = ref(false)
const status = ref('Select scenario to begin')
const ws = ref(null)
const recentDetections = ref([])
const biodiversity = ref(0)
const conservation = ref(0)
const speciesCount = ref(0)
const totalDetections = ref(0)

let detectionIdCounter = 0

const speciesIcons = {
  'Laughing Kookaburra': '🦆',
  'Australian Magpie': '🦅',
  'Galah': '🦜',
  'Koala': '🐨',
  'Dingo': '🐺'
}

const getSpeciesIcon = (species) => {
  return speciesIcons[species] || '🦜'
}

const toggle = () => {
  if (isMonitoring.value) {
    stop()
  } else {
    start()
  }
}

const start = async () => {
  if (!selectedScenario.value) return
  
  status.value = 'Connecting...'
  
  try {
    ws.value = new WebSocket(`ws://localhost:8002/ws/${selectedScenario.value}`)
    
    ws.value.onopen = () => {
      isMonitoring.value = true
      status.value = `Monitoring ${selectedScenario.value.replace('_', ' ').toUpperCase()}`
    }
    
    ws.value.onmessage = (event) => {
      const data = JSON.parse(event.data)
      handleWildlifeData(data)
    }
    
    ws.value.onerror = () => {
      status.value = 'Connection failed - start server first'
      isMonitoring.value = false
    }
    
    ws.value.onclose = () => {
      if (isMonitoring.value) {
        status.value = 'Session complete'
      }
      isMonitoring.value = false
    }
  } catch (error) {
    status.value = 'Failed to connect'
  }
}

const stop = () => {
  if (ws.value) {
    ws.value.close()
  }
  isMonitoring.value = false
  status.value = 'Stopped'
}

const reset = () => {
  stop()
  recentDetections.value = []
  biodiversity.value = 0
  conservation.value = 0
  speciesCount.value = 0
  totalDetections.value = 0
  detectionIdCounter = 0
  status.value = 'Ready to begin'
}

const handleWildlifeData = (data) => {
  if (data.species_detected) {
    // Add new detection
    const detection = {
      id: ++detectionIdCounter,
      species: data.common_name,
      time: data.monitoring_time?.toFixed(1) || '0.0',
      isNew: true
    }
    
    recentDetections.value.unshift(detection)
    
    // Remove 'new' class after animation
    setTimeout(() => {
      detection.isNew = false
    }, 500)
    
    // Keep only recent detections
    if (recentDetections.value.length > 8) {
      recentDetections.value.pop()
    }
  }
  
  // Update metrics
  if (data.biodiversity_index !== undefined) biodiversity.value = data.biodiversity_index
  if (data.conservation_score !== undefined) conservation.value = data.conservation_score
  if (data.total_detections !== undefined) totalDetections.value = data.total_detections
  
  // Count unique species
  const uniqueSpecies = new Set(recentDetections.value.map(d => d.species))
  speciesCount.value = uniqueSpecies.size
}
</script>

<style scoped>
.bush-ears-demo {
  background: #000;
  color: #fff;
  font-family: 'Monaco', 'Menlo', monospace;
  padding: 20px;
  border: 1px solid #333;
  font-size: 11px;
  max-width: 700px;
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
  font-size: 9px;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.status.monitoring {
  color: #00ff00;
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
  font-size: 10px;
  cursor: pointer;
}

button:hover:not(:disabled) {
  border-color: #666;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.main-area {
  display: flex;
  gap: 15px;
}

.detections {
  flex: 1;
}

.detections h4 {
  font-size: 12px;
  margin-bottom: 10px;
  color: #ccc;
  font-weight: normal;
}

.detection-list {
  max-height: 200px;
  overflow-y: auto;
}

.detection {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px;
  border-bottom: 1px solid #333;
  font-size: 10px;
  transition: background 0.5s;
}

.detection.new {
  background: #333;
}

.species-icon {
  font-size: 14px;
}

.detection-info strong {
  display: block;
  font-size: 11px;
}

.detection-time {
  font-size: 9px;
  color: #666;
}

.metrics {
  display: grid;
  grid-template-rows: repeat(4, 1fr);
  gap: 10px;
  width: 140px;
}

.metric {
  text-align: center;
  border: 1px solid #333;
  padding: 8px;
}

.metric .label {
  font-size: 8px;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.metric .value {
  font-size: 14px;
  margin-top: 3px;
  font-weight: normal;
}
</style>
