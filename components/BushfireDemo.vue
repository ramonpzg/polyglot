<template>
  <div class="bushfire-demo">
    <div class="demo-header">
      <h3>🔥 Bushfire Simulation</h3>
      <div class="status" :class="{ 'active': isRunning }">
        {{ status }}
      </div>
    </div>
    
    <div class="controls">
      <select v-model="dangerLevel" :disabled="isRunning">
        <option value="moderate">Moderate</option>
        <option value="high">High</option>
        <option value="very_high">Very High</option>
        <option value="severe">Severe</option>
        <option value="extreme">Extreme</option>
        <option value="catastrophic">Catastrophic</option>
      </select>
      <button @click="toggle" :disabled="!canStart && !isRunning">
        {{ isRunning ? 'STOP' : 'START' }}
      </button>
      <button @click="reset" :disabled="isRunning">RESET</button>
    </div>
    
    <div class="main-area">
      <div class="simulation">
        <canvas ref="canvas" width="320" height="320"></canvas>
        <div class="legend">
          <div class="legend-item">
            <div class="color" style="background: white;"></div>
            <span>Empty</span>
          </div>
          <div class="legend-item">
            <div class="color" style="background: green;"></div>
            <span>Vegetation</span>
          </div>
          <div class="legend-item">
            <div class="color" style="background: red;"></div>
            <span>Burning</span>
          </div>
          <div class="legend-item">
            <div class="color" style="background: #333;"></div>
            <span>Burnt</span>
          </div>
        </div>
      </div>
      
      <div v-if="stats" class="stats">
        <div class="stat">
          <div class="label">Step</div>
          <div class="value">{{ stats.step }}</div>
        </div>
        <div class="stat">
          <div class="label">Fire Spread</div>
          <div class="value">{{ stats.fire_spread_pct.toFixed(1) }}%</div>
        </div>
        <div class="stat">
          <div class="label">Active Fires</div>
          <div class="value">{{ stats.active_fire_pct.toFixed(1) }}%</div>
        </div>
        <div class="stat">
          <div class="label">Burnt</div>
          <div class="value">{{ stats.burnt.toLocaleString() }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'

const dangerLevel = ref('severe')
const isRunning = ref(false)
const status = ref('Ready to simulate')
const stats = ref(null)
const ws = ref(null)
const canvas = ref(null)

const canStart = computed(() => {
  return dangerLevel.value && !isRunning.value
})

let ctx = null
const size = 80  // Match web UI
const cellSize = 4  // Adjusted for better fit
const colors = ['white', 'green', 'red', '#333']

const toggle = () => {
  if (isRunning.value) {
    stop()
  } else {
    start()
  }
}

const start = async () => {
  if (!dangerLevel.value) return
  
  status.value = 'Connecting...'
  
  try {
    ws.value = new WebSocket(`ws://localhost:8001/ws/${dangerLevel.value}`)
    
    ws.value.onopen = () => {
      isRunning.value = true
      status.value = `Simulating ${dangerLevel.value.toUpperCase().replace('_', ' ')}`
    }
    
    ws.value.onmessage = (event) => {
      const data = JSON.parse(event.data)
      updateVisualization(data)
    }
    
    ws.value.onerror = () => {
      status.value = 'Connection failed - start server first'
      isRunning.value = false
    }
    
    ws.value.onclose = () => {
      if (isRunning.value) {
        status.value = 'Simulation complete'
      }
      isRunning.value = false
    }
  } catch (error) {
    status.value = 'Failed to connect'
  }
}

const stop = () => {
  if (ws.value) {
    ws.value.close()
  }
  isRunning.value = false
  status.value = 'Stopped'
}

const reset = () => {
  stop()
  stats.value = null
  if (ctx) {
    ctx.fillStyle = 'black'
    ctx.fillRect(0, 0, canvas.value.width, canvas.value.height)
  }
  status.value = 'Ready to simulate'
}

const updateVisualization = (data) => {
  stats.value = data.stats
  
  if (!ctx) return
  
  // Draw the simulation grid
  const state = data.state
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const cellValue = state[y * size + x]
      ctx.fillStyle = colors[cellValue]
      ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize)
    }
  }
}

onMounted(() => {
  nextTick(() => {
    if (canvas.value) {
      ctx = canvas.value.getContext('2d')
      ctx.fillStyle = 'black'
      ctx.fillRect(0, 0, canvas.value.width, canvas.value.height)
    }
  })
})

onUnmounted(() => {
  stop()
})
</script>

<style scoped>
.bushfire-demo {
  background: #000;
  color: #fff;
  font-family: 'Monaco', 'Menlo', monospace;
  padding: 20px;
  border: 1px solid #333;
  font-size: 11px;
  max-width: 600px;
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

.status.active {
  color: #ff6b6b;
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

.simulation {
  flex: 1;
}

.simulation canvas {
  background: #111;
  border: 1px solid #333;
}

.legend {
  display: flex;
  gap: 10px;
  margin-top: 8px;
  font-size: 9px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 3px;
}

.color {
  width: 8px;
  height: 8px;
  border: 1px solid #333;
}

.stats {
  display: grid;
  grid-template-rows: repeat(4, 1fr);
  gap: 8px;
  width: 120px;
}

.stat {
  text-align: center;
  border: 1px solid #333;
  padding: 6px;
}

.stat .label {
  font-size: 8px;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.stat .value {
  font-size: 12px;
  margin-top: 2px;
}
</style>
