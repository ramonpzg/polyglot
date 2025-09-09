<template>
  <div class="subway-map-container">
    <svg
      :viewBox="`0 0 ${width} ${height}`"
      preserveAspectRatio="xMidYMid meet"
    >
      <defs>
        <!-- Define gradients for each line -->
        <linearGradient id="python-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" style="stop-color: #3776ab; stop-opacity: 1" />
          <stop offset="100%" style="stop-color: #ffd43b; stop-opacity: 1" />
        </linearGradient>
        <linearGradient id="js-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" style="stop-color: #f7df1e; stop-opacity: 1" />
          <stop offset="100%" style="stop-color: #323330; stop-opacity: 1" />
        </linearGradient>
        <linearGradient id="rust-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" style="stop-color: #ce422b; stop-opacity: 1" />
          <stop offset="100%" style="stop-color: #000000; stop-opacity: 1" />
        </linearGradient>
        <linearGradient id="cpp-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" style="stop-color: #00599c; stop-opacity: 1" />
          <stop offset="100%" style="stop-color: #004482; stop-opacity: 1" />
        </linearGradient>
        <linearGradient id="zig-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" style="stop-color: #f7a41d; stop-opacity: 1" />
          <stop offset="100%" style="stop-color: #ec9006; stop-opacity: 1" />
        </linearGradient>
      </defs>

      <!-- Draw the lines -->
      <g class="lines">
        <path
          v-for="line in lines"
          :key="line.id"
          :d="line.path"
          :stroke="`url(#${line.gradient})`"
          stroke-width="4"
          fill="none"
          opacity="0.8"
          class="subway-line"
          :class="{ 'active-line': hoveredLine === line.id }"
        />
      </g>

      <!-- Draw stations -->
      <g class="stations">
        <g
          v-for="station in stations"
          :key="station.id"
          class="station-group"
          @click="navigateTo(station.slide)"
          @mouseenter="hoveredStation = station.id"
          @mouseleave="hoveredStation = null"
        >
          <!-- Station circle -->
          <circle
            :cx="station.x"
            :cy="station.y"
            :r="station.interchange ? 12 : 8"
            :fill="station.color"
            stroke="white"
            stroke-width="2"
            class="station-circle"
            :class="{ 'active-station': hoveredStation === station.id }"
          />

          <!-- Station label -->
          <text
            :x="station.x"
            :y="station.y + (station.labelBelow ? 25 : -15)"
            text-anchor="middle"
            class="station-label"
            :class="{ 'active-label': hoveredStation === station.id }"
          >
            {{ station.name }}
          </text>

          <!-- Slide number indicator -->
          <text
            v-if="hoveredStation === station.id"
            :x="station.x"
            :y="station.y + (station.labelBelow ? 40 : -30)"
            text-anchor="middle"
            class="slide-indicator"
          >
            Slide {{ station.slide }}
          </text>
        </g>
      </g>

      <!-- Legend -->
      <g class="legend" transform="translate(20, 20)">
        <rect
          x="0"
          y="0"
          width="150"
          height="120"
          fill="rgba(0,0,0,0.7)"
          rx="5"
        />
        <text x="75" y="20" text-anchor="middle" class="legend-title">
          Language Lines
        </text>
        <g
          v-for="(legend, i) in legendItems"
          :key="legend.id"
          :transform="`translate(10, ${35 + i * 20})`"
        >
          <line
            x1="0"
            y1="0"
            x2="25"
            y2="0"
            :stroke="`url(#${legend.gradient})`"
            stroke-width="3"
          />
          <text x="30" y="4" class="legend-text">{{ legend.name }}</text>
        </g>
      </g>
    </svg>
  </div>
</template>

<script setup>
import { ref } from "vue";

const width = 900;
const height = 500;
const hoveredStation = ref(null);
const hoveredLine = ref(null);

// Define the stations with their positions and metadata
const stations = [
  // Python Hub (center)
  {
    id: "hub",
    name: "Python Central",
    x: 450,
    y: 250,
    slide: 4,
    color: "#3776ab",
    interchange: true,
    labelBelow: true,
  },

  // JavaScript Line
  {
    id: "js-intro",
    name: "WebSocket Tango",
    x: 250,
    y: 150,
    slide: 10,
    color: "#f7df1e",
    labelBelow: false,
  },
  {
    id: "js-tools",
    name: "Browser Ecosystem",
    x: 350,
    y: 150,
    slide: 11,
    color: "#f7df1e",
    labelBelow: false,
  },
  {
    id: "js-demo",
    name: "VisFlow Demo",
    x: 450,
    y: 150,
    slide: 12,
    color: "#f7df1e",
    labelBelow: false,
  },
  {
    id: "js-perf",
    name: "JS Performance",
    x: 550,
    y: 150,
    slide: 14,
    color: "#f7df1e",
    labelBelow: false,
  },

  // Rust Line
  {
    id: "rust-intro",
    name: "Rust Invasion",
    x: 250,
    y: 250,
    slide: 19,
    color: "#ce422b",
    labelBelow: true,
  },
  {
    id: "rust-pyo3",
    name: "PyO3 Magic",
    x: 350,
    y: 250,
    slide: 20,
    color: "#ce422b",
    labelBelow: true,
  },
  {
    id: "rust-demo",
    name: "PixelFlow Demo",
    x: 550,
    y: 250,
    slide: 22,
    color: "#ce422b",
    labelBelow: true,
  },
  {
    id: "rust-perf",
    name: "Rust Numbers",
    x: 650,
    y: 250,
    slide: 24,
    color: "#ce422b",
    labelBelow: true,
  },

  // C++ Line
  {
    id: "cpp-intro",
    name: "C++ Reality",
    x: 250,
    y: 350,
    slide: 29,
    color: "#00599c",
    labelBelow: true,
  },
  {
    id: "cpp-demo",
    name: "Fire Danger",
    x: 350,
    y: 350,
    slide: 30,
    color: "#00599c",
    labelBelow: true,
  },
  {
    id: "cpp-modern",
    name: "C++23 Features",
    x: 450,
    y: 350,
    slide: 32,
    color: "#00599c",
    labelBelow: true,
  },

  // Zig Line
  {
    id: "zig-demo",
    name: "Zig Simplicity",
    x: 550,
    y: 350,
    slide: 33,
    color: "#f7a41d",
    labelBelow: true,
  },
  {
    id: "zig-why",
    name: "Why Zig?",
    x: 650,
    y: 350,
    slide: 36,
    color: "#f7a41d",
    labelBelow: true,
  },

  // AI & Architecture
  {
    id: "ai-hub",
    name: "AI Assistance",
    x: 750,
    y: 250,
    slide: 39,
    color: "#9333ea",
    interchange: true,
    labelBelow: true,
  },
  {
    id: "arch",
    name: "Architecture",
    x: 750,
    y: 150,
    slide: 45,
    color: "#10b981",
    labelBelow: false,
  },
];

// Define the subway lines
const lines = [
  {
    id: "python-main",
    gradient: "python-gradient",
    path: "M 150,250 L 850,250",
  },
  {
    id: "js-line",
    gradient: "js-gradient",
    path: "M 250,150 L 550,150 Q 600,150 600,200 L 600,250",
  },
  {
    id: "rust-line",
    gradient: "rust-gradient",
    path: "M 250,250 L 650,250",
  },
  {
    id: "cpp-line",
    gradient: "cpp-gradient",
    path: "M 250,350 L 450,350 Q 500,350 500,300 L 500,250",
  },
  {
    id: "zig-line",
    gradient: "zig-gradient",
    path: "M 450,350 L 650,350",
  },
  {
    id: "ai-line",
    gradient: "python-gradient",
    path: "M 750,150 L 750,350",
  },
];

// Legend items
const legendItems = [
  { id: "python", name: "Python", gradient: "python-gradient" },
  { id: "js", name: "JavaScript", gradient: "js-gradient" },
  { id: "rust", name: "Rust", gradient: "rust-gradient" },
  { id: "cpp", name: "C++", gradient: "cpp-gradient" },
  { id: "zig", name: "Zig", gradient: "zig-gradient" },
];

// Navigation function
const navigateTo = (slideNumber) => {
  if (typeof $slidev !== "undefined" && $slidev?.nav?.go) {
    $slidev.nav.go(slideNumber);
  }
};
</script>

<style scoped>
.subway-map-container {
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

.subway-line {
  transition: all 0.3s ease;
}

.subway-line.active-line {
  stroke-width: 6;
  opacity: 1;
}

.station-group {
  cursor: pointer;
}

.station-circle {
  transition: all 0.3s ease;
}

.station-circle.active-station {
  r: 14;
  filter: drop-shadow(0 0 8px currentColor);
}

.station-label {
  fill: #e5e7eb;
  font-size: 12px;
  font-weight: 600;
  pointer-events: none;
  transition: all 0.3s ease;
}

.station-label.active-label {
  fill: #ffffff;
  font-size: 14px;
}

.slide-indicator {
  fill: #60a5fa;
  font-size: 10px;
  font-weight: 400;
  pointer-events: none;
  animation: fadeIn 0.3s ease;
}

.legend-title {
  fill: #ffffff;
  font-size: 14px;
  font-weight: bold;
}

.legend-text {
  fill: #e5e7eb;
  font-size: 12px;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Dark mode adjustments */
@media (prefers-color-scheme: dark) {
  .station-label {
    fill: #d1d5db;
  }

  .station-label.active-label {
    fill: #ffffff;
  }
}
</style>
