<template>
  <div class="performance-meter">
    <div class="meter-header">
      <h3 class="meter-title">Performance Comparison</h3>
      <div class="meter-legend">
        <div class="legend-item">
          <span class="legend-dot python"></span>
          <span class="legend-label">Python</span>
        </div>
        <div class="legend-item">
          <span class="legend-dot javascript"></span>
          <span class="legend-label">JavaScript</span>
        </div>
      </div>
    </div>

    <div class="test-results">
      <div
        v-for="(test, index) in tests"
        :key="index"
        class="test-row"
        :class="{ appear: appeared[index] }"
      >
        <div class="test-name">{{ test.name }}</div>

        <div class="test-bars">
          <!-- Python bar -->
          <div class="bar-container python-bar">
            <div
              v-if="test.python !== null"
              class="bar"
              :style="{ width: getPythonWidth(test) + '%' }"
            >
              <span class="time-label">{{ formatTime(test.python) }}</span>
            </div>
            <div v-else class="not-applicable">N/A</div>
          </div>

          <!-- JavaScript bar -->
          <div class="bar-container javascript-bar">
            <div
              v-if="test.javascript !== null"
              class="bar"
              :style="{ width: getJavaScriptWidth(test) + '%' }"
            >
              <span class="time-label">{{ formatTime(test.javascript) }}</span>
            </div>
            <div v-else class="not-applicable">N/A</div>
          </div>

          <!-- Winner indicator -->
          <div class="winner-indicator">
            <span v-if="getWinner(test)" :class="getWinnerClass(test)">
              {{ getSpeedup(test) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showSummary" class="meter-summary">
      <div class="summary-item">
        <span class="summary-label">Python wins:</span>
        <span class="summary-value">{{ pythonWins }}</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">JavaScript wins:</span>
        <span class="summary-value">{{ javascriptWins }}</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">Ties:</span>
        <span class="summary-value">{{ ties }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";

const props = defineProps({
  tests: {
    type: Array,
    required: true,
  },
  showSummary: {
    type: Boolean,
    default: true,
  },
  animationDelay: {
    type: Number,
    default: 100,
  },
});

const appeared = ref({});

// Calculate the maximum time for scaling
const maxTime = computed(() => {
  let max = 0;
  props.tests.forEach((test) => {
    if (test.python !== null && test.python > max) max = test.python;
    if (test.javascript !== null && test.javascript > max)
      max = test.javascript;
  });
  return max || 1;
});

// Calculate bar widths as percentages
const getPythonWidth = (test) => {
  if (test.python === null) return 0;
  return (test.python / maxTime.value) * 80; // 80% max width for visual balance
};

const getJavaScriptWidth = (test) => {
  if (test.javascript === null) return 0;
  return (test.javascript / maxTime.value) * 80;
};

// Format time display
const formatTime = (time) => {
  if (time === null) return "N/A";
  if (time < 0.001) return "<1ms";
  if (time < 1) return `${Math.round(time * 1000)}ms`;
  return `${time.toFixed(2)}s`;
};

// Determine winner for each test
const getWinner = (test) => {
  if (test.python === null || test.javascript === null) {
    return test.python === null ? "javascript" : "python";
  }

  const ratio =
    Math.abs(test.python - test.javascript) /
    Math.min(test.python, test.javascript);
  if (ratio < 0.1) return "tie"; // Within 10% is considered a tie

  return test.python < test.javascript ? "python" : "javascript";
};

// Get winner class for styling
const getWinnerClass = (test) => {
  const winner = getWinner(test);
  return {
    "python-wins": winner === "python",
    "javascript-wins": winner === "javascript",
    tie: winner === "tie",
  };
};

// Calculate speedup factor
const getSpeedup = (test) => {
  const winner = getWinner(test);

  if (winner === "tie") return "≈";
  if (test.python === null || test.javascript === null) return "✓";

  const factor =
    winner === "python"
      ? test.javascript / test.python
      : test.python / test.javascript;

  if (factor > 100) return `${Math.round(factor)}x`;
  if (factor > 10) return `${factor.toFixed(1)}x`;
  return `${factor.toFixed(2)}x`;
};

// Summary statistics
const pythonWins = computed(() => {
  return props.tests.filter((test) => getWinner(test) === "python").length;
});

const javascriptWins = computed(() => {
  return props.tests.filter((test) => getWinner(test) === "javascript").length;
});

const ties = computed(() => {
  return props.tests.filter((test) => getWinner(test) === "tie").length;
});

// Animate appearance
onMounted(() => {
  props.tests.forEach((_, index) => {
    setTimeout(() => {
      appeared.value[index] = true;
    }, index * props.animationDelay);
  });
});
</script>

<style scoped>
.performance-meter {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
  background: rgba(30, 41, 59, 0.3);
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.1);
}

.meter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
}

.meter-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #e2e8f0;
  margin: 0;
}

.meter-legend {
  display: flex;
  gap: 20px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 3px;
}

.legend-dot.python {
  background: linear-gradient(135deg, #3776ab, #ffd43b);
}

.legend-dot.javascript {
  background: linear-gradient(135deg, #f7df1e, #323330);
}

.legend-label {
  font-size: 0.875rem;
  color: #94a3b8;
}

.test-results {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.test-row {
  opacity: 0;
  transform: translateX(-20px);
  transition: all 0.5s ease;
}

.test-row.appear {
  opacity: 1;
  transform: translateX(0);
}

.test-name {
  font-size: 0.875rem;
  color: #cbd5e1;
  margin-bottom: 8px;
  font-weight: 500;
}

.test-bars {
  display: flex;
  flex-direction: column;
  gap: 6px;
  position: relative;
}

.bar-container {
  height: 28px;
  background: rgba(71, 85, 105, 0.2);
  border-radius: 4px;
  position: relative;
  overflow: hidden;
}

.bar {
  height: 100%;
  display: flex;
  align-items: center;
  padding: 0 8px;
  border-radius: 4px;
  transition: width 0.8s ease;
}

.python-bar .bar {
  background: linear-gradient(90deg, #3776ab, #4b8bbe);
}

.javascript-bar .bar {
  background: linear-gradient(90deg, #f7df1e, #e5c91e);
}

.time-label {
  font-size: 0.75rem;
  color: #1e293b;
  font-weight: 600;
  white-space: nowrap;
}

.not-applicable {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  font-size: 0.75rem;
  color: #64748b;
  font-style: italic;
}

.winner-indicator {
  position: absolute;
  right: -50px;
  top: 50%;
  transform: translateY(-50%);
  width: 40px;
  text-align: center;
}

.winner-indicator span {
  font-size: 0.875rem;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
}

.python-wins {
  color: #3b82f6;
  background: rgba(59, 130, 246, 0.1);
}

.javascript-wins {
  color: #eab308;
  background: rgba(234, 179, 8, 0.1);
}

.tie {
  color: #64748b;
}

.meter-summary {
  display: flex;
  justify-content: space-around;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid rgba(148, 163, 184, 0.1);
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.summary-label {
  font-size: 0.75rem;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.summary-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #e2e8f0;
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .meter-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .winner-indicator {
    right: -40px;
  }
}
</style>
