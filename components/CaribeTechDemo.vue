<template>
  <div class="caribetech-demo">
    <div class="demo-header">
      <h3>🌀 CaribeTech</h3>
      <div class="status" :class="{ 'monitoring': isMonitoring }">
        {{ status }}
      </div>
    </div>
    
    <div class="controls">
      <select v-model="selectedRegion" :disabled="isMonitoring">
        <option value="dominican_republic">Dominican Republic</option>
        <option value="puerto_rico">Puerto Rico</option>
        <option value="jamaica">Jamaica</option>
        <option value="caribbean_wide">Caribbean Wide</option>
      </select>
      <button @click="toggle" :disabled="!selectedRegion">
        {{ isMonitoring ? 'STOP' : 'START' }}
      </button>
      <button @click="reset" :disabled="isMonitoring">RESET</button>
    </div>
    
    <div class="main-area">
      <div class="threats">
        <h4>Hurricane Threats</h4>
        <div class="threat-list">
          <div v-for="threat in activeTreats" 
               :key="threat.id" 
               class="threat"
               :class="threat.level.toLowerCase()">
            <span class="storm-icon">🌀</span>
            <div class="threat-info">
              <strong>{{ threat.name }}</strong>
              <div class="threat-details">
                Cat {{ threat.category }} • {{ threat.distance }}km • {{ threat.speed }}km/h
              </div>
            </div>
            <div class="threat-level">{{ threat.level }}</div>
          </div>
        </div>
      </div>
      
      <div class="metrics">
        <div class="metric">
          <div class="label">Active</div>
          <div class="value">{{ activeStorms }}</div>
        </div>
        <div class="metric">
          <div class="label">Distance</div>
          <div class="value">{{ closestDistance }}km</div>
        </div>
        <div class="metric">
          <div class="label">Speed</div>
          <div class="value">{{ zigSpeedup }}x</div>
        </div>
        <div class="metric">
          <div class="label">Threats</div>
          <div class="value">{{ totalThreats }}</div>
        </div>
      </div>
    </div>
    
    <div class="performance">
      <div class="perf-label">Zig Performance:</div>
      <div class="perf-bar">
        <div class="perf-fill" :style="{ width: performancePercent + '%' }"></div>
        <span class="perf-text">{{ calculationsPerSec.toLocaleString() }} calc/sec</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const selectedRegion = ref('dominican_republic')
const isMonitoring = ref(false)
const status = ref('Select region to monitor')
const ws = ref(null)
const activeTreats = ref([])
const activeStorms = ref(0)
const closestDistance = ref(999)
const zigSpeedup = ref(6.8)
const totalThreats = ref(0)
const calculationsPerSec = ref(125000)
const performancePercent = ref(68)

let threatIdCounter = 0
let simulationInterval = null

const toggle = () => {
  if (isMonitoring.value) {
    stop()
  } else {
    start()
  }
}

const start = async () => {
  if (!selectedRegion.value) return
  
  status.value = 'Connecting...'
  isMonitoring.value = true
  status.value = `Monitoring ${selectedRegion.value.replace('_', ' ').toUpperCase()}`
  
  // Simulate real-time hurricane data
  simulationInterval = setInterval(() => {
    generateHurricaneData()
  }, 2000)
  
  // Initial data
  generateHurricaneData()
}

const stop = () => {
  if (simulationInterval) {
    clearInterval(simulationInterval)
    simulationInterval = null
  }
  isMonitoring.value = false
  status.value = 'Stopped'
}

const reset = () => {
  stop()
  activeTreats.value = []
  activeStorms.value = 0
  closestDistance.value = 999
  totalThreats.value = 0
  threatIdCounter = 0
  status.value = 'Ready to monitor'
}

const generateHurricaneData = () => {
  const stormNames = ['Elena', 'Fernando', 'Gabriela', 'Hernan', 'Isabel']
  const threatLevels = ['LOW', 'MODERATE', 'HIGH', 'EXTREME']
  
  // Randomly add or update threats
  if (Math.random() > 0.3 && activeTreats.value.length < 4) {
    const threat = {
      id: ++threatIdCounter,
      name: stormNames[Math.floor(Math.random() * stormNames.length)],
      category: Math.floor(Math.random() * 5) + 1,
      distance: Math.floor(Math.random() * 800) + 100,
      speed: Math.floor(Math.random() * 50) + 120,
      level: threatLevels[Math.floor(Math.random() * threatLevels.length)]
    }
    
    activeTreats.value.unshift(threat)
    
    // Remove old threats
    if (activeTreats.value.length > 3) {
      activeTreats.value.pop()
    }
  }
  
  // Update metrics
  activeStorms.value = activeTreats.value.length
  if (activeTreats.value.length > 0) {
    closestDistance.value = Math.min(...activeTreats.value.map(t => t.distance))
  }
  totalThreats.value = threatIdCounter
  
  // Simulate performance variations
  calculationsPerSec.value = 125000 + Math.floor(Math.random() * 25000)
  performancePercent.value = 60 + Math.floor(Math.random() * 30)
}
</script>

<style scoped>
.caribetech-demo {
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
  margin-bottom: 15px;
}

.threats {
  flex: 1;
}

.threats h4 {
  font-size: 12px;
  margin-bottom: 10px;
  color: #ccc;
  font-weight: normal;
}

.threat-list {
  max-height: 200px;
  overflow-y: auto;
}

.threat {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px;
  border-bottom: 1px solid #333;
  font-size: 10px;
}

.threat.extreme {
  border-left: 2px solid #ff4757;
}

.threat.high {
  border-left: 2px solid #ff6348;
}

.threat.moderate {
  border-left: 2px solid #ffa502;
}

.threat.low {
  border-left: 2px solid #2ed573;
}

.storm-icon {
  font-size: 14px;
}

.threat-info {
  flex: 1;
}

.threat-info strong {
  display: block;
  font-size: 11px;
}

.threat-details {
  font-size: 9px;
  color: #666;
}

.threat-level {
  font-size: 8px;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 1px;
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

.performance {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 0;
  border-top: 1px solid #333;
}

.perf-label {
  font-size: 9px;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 1px;
  width: 100px;
}

.perf-bar {
  flex: 1;
  height: 12px;
  background: #333;
  position: relative;
  border: 1px solid #333;
}

.perf-fill {
  height: 100%;
  background: #00ff00;
  transition: width 0.5s;
}

.perf-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 8px;
  color: #fff;
  text-shadow: 1px 1px 1px #000;
}
</style>
