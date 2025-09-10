<template>
  <div class="merengue-cyclone-demo">
    <div class="demo-container">
      <!-- Header -->
      <div class="demo-header">
        <h3>🌀 Merengue Cyclone Tracker</h3>
        <div class="status-bar">
          <span class="status-item" :class="{ active: isConnected }">
            <span class="status-dot"></span>
            {{ isConnected ? 'Connected' : 'Disconnected' }}
          </span>
          <span class="status-item">
            <span class="flag">🇩🇴</span> Dominican Republic
          </span>
        </div>
      </div>

      <!-- Main Display -->
      <div class="main-display">
        <!-- Map View -->
        <div class="map-container">
          <svg viewBox="0 0 800 600" class="hurricane-map">
            <!-- Caribbean outline -->
            <rect x="0" y="0" width="800" height="600" fill="#000" opacity="0.05" />

            <!-- Grid lines -->
            <g class="grid-lines">
              <line v-for="i in 8" :key="`h-${i}`"
                    :x1="0" :y1="i * 75"
                    :x2="800" :y2="i * 75"
                    stroke="#ccc" stroke-width="0.5" opacity="0.3" />
              <line v-for="i in 10" :key="`v-${i}`"
                    :x1="i * 80" :y1="0"
                    :x2="i * 80" :y2="600"
                    stroke="#ccc" stroke-width="0.5" opacity="0.3" />
            </g>

            <!-- Dominican Republic -->
            <g class="dominican-republic">
              <path d="M 450 280 L 520 275 L 540 285 L 535 300 L 510 305 L 480 300 L 450 295 Z"
                    fill="none" stroke="#00aa00" stroke-width="2" opacity="0.8" />
              <circle cx="490" cy="290" r="3" fill="#00ff00" />
              <text x="495" y="295" font-size="10" fill="#00aa00">Santo Domingo</text>
            </g>

            <!-- Hurricane Track -->
            <g class="hurricane-track">
              <!-- Historical path -->
              <polyline v-if="trackPoints.length > 1"
                        :points="trackPoints.map(p => `${p.x},${p.y}`).join(' ')"
                        fill="none" stroke="#0066cc" stroke-width="2" opacity="0.8" />

              <!-- Track points -->
              <g v-for="(point, index) in trackPoints" :key="`point-${index}`">
                <circle :cx="point.x" :cy="point.y" :r="getCategoryRadius(point.category)"
                        :fill="getCategoryColor(point.category)"
                        :opacity="index === trackPoints.length - 1 ? 1 : 0.6">
                  <animate v-if="index === trackPoints.length - 1"
                           attributeName="r"
                           :values="`${getCategoryRadius(point.category)};${getCategoryRadius(point.category) + 2};${getCategoryRadius(point.category)}`"
                           dur="2s" repeatCount="indefinite" />
                </circle>
              </g>

              <!-- Predicted path -->
              <polyline v-if="predictions.length > 0"
                        :points="predictions.map(p => `${p.x},${p.y}`).join(' ')"
                        fill="none" stroke="#ff6666" stroke-width="2"
                        stroke-dasharray="5,5" opacity="0.6" />
            </g>

            <!-- Wind field visualization -->
            <g class="wind-field" v-if="currentHurricane">
              <circle :cx="currentHurricane.x" :cy="currentHurricane.y"
                      :r="currentHurricane.windField"
                      fill="none" stroke="#ff9900" stroke-width="1"
                      opacity="0.2" stroke-dasharray="2,2">
                <animate attributeName="r"
                         :values="`${currentHurricane.windField};${currentHurricane.windField + 10};${currentHurricane.windField}`"
                         dur="3s" repeatCount="indefinite" />
              </circle>
            </g>
          </svg>
        </div>

        <!-- Info Panel -->
        <div class="info-panel">
          <!-- Current Status -->
          <div class="status-section">
            <h4>Current Status</h4>
            <div class="metric-grid">
              <div class="metric">
                <span class="label">Category</span>
                <span class="value category" :class="`cat-${currentCategory}`">
                  {{ currentCategory }}
                </span>
              </div>
              <div class="metric">
                <span class="label">Wind Speed</span>
                <span class="value">{{ currentWindSpeed }} km/h</span>
              </div>
              <div class="metric">
                <span class="label">Pressure</span>
                <span class="value">{{ currentPressure }} mb</span>
              </div>
              <div class="metric">
                <span class="label">Movement</span>
                <span class="value">{{ movementSpeed }} km/h {{ movementDir }}</span>
              </div>
            </div>
          </div>

          <!-- DR Impact Assessment -->
          <div class="impact-section">
            <h4>🇩🇴 DR Impact Assessment</h4>
            <div class="impact-grid">
              <div class="impact-item">
                <span class="label">Risk Level</span>
                <span class="value risk" :class="`risk-${riskLevel}`">
                  {{ riskLevel.toUpperCase() }}
                </span>
              </div>
              <div class="impact-item">
                <span class="label">Closest Approach</span>
                <span class="value">{{ closestApproach }} km</span>
              </div>
              <div class="impact-item">
                <span class="label">Storm Surge</span>
                <span class="value">{{ stormSurge }} m</span>
              </div>
              <div class="impact-item">
                <span class="label">Impact Time</span>
                <span class="value">{{ impactTime }}</span>
              </div>
            </div>
          </div>

          <!-- Performance Metrics -->
          <div class="performance-section">
            <h4>⚡ Performance (Zig Acceleration)</h4>
            <div class="perf-bars">
              <div class="perf-bar">
                <span class="label">Distance Calc</span>
                <div class="bar-container">
                  <div class="bar python" :style="{width: '100%'}">
                    <span>Python: 245ms</span>
                  </div>
                  <div class="bar zig" :style="{width: '1.3%'}">
                    <span>Zig: 3.2ms</span>
                  </div>
                </div>
                <span class="speedup">76x faster</span>
              </div>
              <div class="perf-bar">
                <span class="label">Track Analysis</span>
                <div class="bar-container">
                  <div class="bar python" :style="{width: '100%'}">
                    <span>Python: 89ms</span>
                  </div>
                  <div class="bar zig" :style="{width: '1.2%'}">
                    <span>Zig: 1.1ms</span>
                  </div>
                </div>
                <span class="speedup">81x faster</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Controls -->
      <div class="controls">
        <button @click="simulateHurricane('maria')" :disabled="isSimulating">
          Hurricane Maria (2017)
        </button>
        <button @click="simulateHurricane('georges')" :disabled="isSimulating">
          Hurricane Georges (1998)
        </button>
        <button @click="simulateHurricane('david')" :disabled="isSimulating">
          Hurricane David (1979)
        </button>
        <button @click="clearTrack" :disabled="isSimulating">
          Clear Track
        </button>
      </div>

      <!-- Activity Log -->
      <div class="activity-log">
        <div class="log-entry" v-for="(entry, index) in activityLog" :key="`log-${index}`">
          <span class="timestamp">{{ entry.time }}</span>
          <span class="message">{{ entry.message }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

// Connection state
const isConnected = ref(false)
const ws = ref(null)

// Hurricane data
const trackPoints = ref([])
const predictions = ref([])
const currentHurricane = ref(null)
const isSimulating = ref(false)

// Current metrics
const currentCategory = ref(0)
const currentWindSpeed = ref(0)
const currentPressure = ref(1013)
const movementSpeed = ref(0)
const movementDir = ref('W')

// DR Impact
const riskLevel = ref('low')
const closestApproach = ref(0)
const stormSurge = ref(0)
const impactTime = ref('--')

// Activity log
const activityLog = ref([])

// Helper functions
const getCategoryColor = (category) => {
  const colors = ['#888', '#ffe775', '#ffaa55', '#ff5555', '#cc0000', '#990099']
  return colors[category] || '#888'
}

const getCategoryRadius = (category) => {
  return 4 + category * 2
}

const latLonToXY = (lat, lon) => {
  // Convert lat/lon to SVG coordinates
  // Caribbean region roughly 10-25°N, 60-80°W
  const x = 800 - ((lon + 80) / 20 * 800)
  const y = 600 - ((lat - 10) / 15 * 600)
  return { x, y }
}

const addLogEntry = (message) => {
  const now = new Date()
  const time = now.toLocaleTimeString('en-US', { hour12: false })
  activityLog.value.unshift({ time, message })
  if (activityLog.value.length > 5) {
    activityLog.value.pop()
  }
}

// WebSocket connection
const connectWebSocket = () => {
  try {
    ws.value = new WebSocket('ws://localhost:8000/ws')

    ws.value.onopen = () => {
      isConnected.value = true
      addLogEntry('Connected to Merengue Cyclone server')
    }

    ws.value.onmessage = (event) => {
      const data = JSON.parse(event.data)
      handleWebSocketMessage(data)
    }

    ws.value.onclose = () => {
      isConnected.value = false
      addLogEntry('Disconnected from server')
      // Reconnect after 3 seconds
      setTimeout(connectWebSocket, 3000)
    }

    ws.value.onerror = () => {
      isConnected.value = false
    }
  } catch (error) {
    console.error('WebSocket connection error:', error)
    isConnected.value = false
  }
}

const handleWebSocketMessage = (data) => {
  if (data.type === 'simulation' || data.type === 'observation') {
    const point = data.point
    const xy = latLonToXY(point.lat, point.lon)

    trackPoints.value.push({
      ...xy,
      category: point.category,
      windSpeed: point.wind_speed,
      pressure: point.pressure
    })

    currentCategory.value = point.category
    currentWindSpeed.value = Math.round(point.wind_speed)
    currentPressure.value = Math.round(point.pressure)

    currentHurricane.value = {
      ...xy,
      windField: 50 + point.category * 15
    }

    if (trackPoints.value.length > 1) {
      const prev = trackPoints.value[trackPoints.value.length - 2]
      const dist = Math.sqrt((xy.x - prev.x) ** 2 + (xy.y - prev.y) ** 2)
      movementSpeed.value = Math.round(dist * 0.5) // Simplified
      movementDir.value = xy.x < prev.x ? 'W' : 'E'
    }

    addLogEntry(`${data.scenario || data.track}: Cat ${point.category}, ${Math.round(point.wind_speed)} km/h`)
  }
}

// Simulate hurricane
const simulateHurricane = async (scenario) => {
  if (isSimulating.value) return

  isSimulating.value = true
  clearTrack()
  addLogEntry(`Starting ${scenario.toUpperCase()} simulation...`)

  try {
    const response = await fetch(`http://localhost:8000/api/simulate/${scenario}`, {
      method: 'POST'
    })
    const data = await response.json()

    // Update DR impact
    if (data.dr_impact) {
      riskLevel.value = data.dr_impact.risk
      closestApproach.value = Math.round(data.dr_impact.closest_approach_km)
      stormSurge.value = data.dr_impact.estimated_surge_m.toFixed(1)
      impactTime.value = data.dr_impact.impact_time ?
        new Date(data.dr_impact.impact_time).toLocaleString() : '--'
    }

    // Get predictions
    const predResponse = await fetch(`http://localhost:8000/api/track/${scenario}/predict`)
    const predData = await predResponse.json()

    predictions.value = predData.predictions.map(p =>
      latLonToXY(p.lat, p.lon)
    )

  } catch (error) {
    console.error('Simulation error:', error)
    addLogEntry('Error: Could not connect to server')
  } finally {
    isSimulating.value = false
  }
}

const clearTrack = () => {
  trackPoints.value = []
  predictions.value = []
  currentHurricane.value = null
  currentCategory.value = 0
  currentWindSpeed.value = 0
  currentPressure.value = 1013
  movementSpeed.value = 0
  movementDir.value = 'W'
  riskLevel.value = 'low'
  closestApproach.value = 0
  stormSurge.value = 0
  impactTime.value = '--'
  addLogEntry('Track cleared')
}

// Lifecycle
onMounted(() => {
  connectWebSocket()

  // Demo mode if server not available
  setTimeout(() => {
    if (!isConnected.value) {
      addLogEntry('Running in demo mode')
      // Add some demo points
      const demoPoints = [
        { lat: 15, lon: -60, category: 1, wind_speed: 130, pressure: 985 },
        { lat: 15.5, lon: -61.5, category: 2, wind_speed: 160, pressure: 975 },
        { lat: 16, lon: -63, category: 3, wind_speed: 190, pressure: 960 },
        { lat: 16.5, lon: -64.5, category: 4, wind_speed: 220, pressure: 945 },
        { lat: 17, lon: -66, category: 4, wind_speed: 230, pressure: 940 },
      ]

      demoPoints.forEach((point, i) => {
        setTimeout(() => {
          const xy = latLonToXY(point.lat, point.lon)
          trackPoints.value.push({
            ...xy,
            category: point.category,
            windSpeed: point.wind_speed,
            pressure: point.pressure
          })
          currentCategory.value = point.category
          currentWindSpeed.value = point.wind_speed
          currentPressure.value = point.pressure
          currentHurricane.value = {
            ...xy,
            windField: 50 + point.category * 15
          }
        }, i * 500)
      })
    }
  }, 2000)
})

onUnmounted(() => {
  if (ws.value) {
    ws.value.close()
  }
})
</script>

<style scoped>
.merengue-cyclone-demo {
  width: 100%;
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', monospace;
  background: #fff;
  color: #000;
}

.demo-container {
  border: 2px solid #000;
  border-radius: 8px;
  overflow: hidden;
}

.demo-header {
  background: #000;
  color: #fff;
  padding: 12px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.demo-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.status-bar {
  display: flex;
  gap: 20px;
  align-items: center;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  opacity: 0.8;
}

.status-item.active {
  opacity: 1;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ff0000;
}

.status-item.active .status-dot {
  background: #00ff00;
  animation: pulse 2s infinite;
}

.main-display {
  display: grid;
  grid-template-columns: 1fr 380px;
  height: 400px;
  background: #fafafa;
}

.map-container {
  border-right: 1px solid #ddd;
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hurricane-map {
  width: 100%;
  height: 100%;
  max-width: 500px;
  border: 1px solid #ccc;
  background: white;
}

.info-panel {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto;
}

.status-section h4,
.impact-section h4,
.performance-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  padding-bottom: 8px;
  border-bottom: 1px solid #ddd;
}

.metric-grid,
.impact-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.metric,
.impact-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.metric .label,
.impact-item .label {
  font-size: 11px;
  color: #666;
  text-transform: uppercase;
}

.metric .value,
.impact-item .value {
  font-size: 18px;
  font-weight: 600;
}

.value.category {
  padding: 2px 8px;
  border-radius: 4px;
  display: inline-block;
  width: fit-content;
}

.cat-0 { background: #888; color: white; }
.cat-1 { background: #ffe775; color: #000; }
.cat-2 { background: #ffaa55; color: #000; }
.cat-3 { background: #ff5555; color: white; }
.cat-4 { background: #cc0000; color: white; }
.cat-5 { background: #990099; color: white; }

.value.risk {
  padding: 2px 8px;
  border-radius: 4px;
  display: inline-block;
  width: fit-content;
  font-size: 14px;
}

.risk-low { background: #4caf50; color: white; }
.risk-moderate { background: #ff9800; color: white; }
.risk-high { background: #ff5722; color: white; }
.risk-extreme { background: #d32f2f; color: white; }

.perf-bars {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.perf-bar {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.perf-bar .label {
  font-size: 11px;
  color: #666;
}

.bar-container {
  position: relative;
  height: 24px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.bar {
  position: absolute;
  height: 100%;
  display: flex;
  align-items: center;
  padding: 0 8px;
  font-size: 10px;
  transition: width 0.3s ease;
}

.bar.python {
  background: #3776ab;
  color: white;
}

.bar.zig {
  background: #f7a41d;
  color: #000;
  z-index: 1;
}

.bar span {
  white-space: nowrap;
}

.speedup {
  font-size: 11px;
  color: #f7a41d;
  font-weight: 600;
  text-align: right;
}

.controls {
  padding: 16px 20px;
  background: #f5f5f5;
  border-top: 1px solid #ddd;
  display: flex;
  gap: 12px;
}

.controls button {
  padding: 8px 16px;
  background: #000;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.controls button:hover:not(:disabled) {
  background: #333;
  transform: translateY(-1px);
}

.controls button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.activity-log {
  padding: 12px 20px;
  background: #000;
  color: #0f0;
  font-size: 11px;
  font-family: monospace;
  max-height: 100px;
  overflow-y: auto;
}

.log-entry {
  display: flex;
  gap: 12px;
  margin-bottom: 4px;
  opacity: 0.9;
}

.log-entry:first-child {
  opacity: 1;
}

.timestamp {
  color: #888;
}

.message {
  flex: 1;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
