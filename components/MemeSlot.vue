<template>
  <div
    class="meme-slot"
    :class="[
      `meme-slot--${type}`,
      {
        'meme-slot--loaded': loaded,
        'meme-slot--animated': animated
      }
    ]"
  >
    <!-- Actual image/gif when src is provided -->
    <div v-if="src" class="meme-content">
      <img
        :src="src"
        :alt="alt || description"
        @load="onLoad"
        @error="onError"
        v-show="loaded && !error"
      />
      <div v-if="!loaded && !error" class="meme-loading">
        <div class="loading-spinner"></div>
        <span>Loading...</span>
      </div>
      <div v-if="error" class="meme-error">
        <span>❌ Failed to load image</span>
      </div>
    </div>

    <!-- Placeholder when no src -->
    <div v-else class="meme-placeholder">
      <div class="placeholder-icon">
        {{ getIcon() }}
      </div>
      <div class="placeholder-text">
        <div class="placeholder-title">{{ title || getDefaultTitle() }}</div>
        <div v-if="description" class="placeholder-description">{{ description }}</div>
        <div v-if="caption" class="placeholder-caption">{{ caption }}</div>
      </div>
      <div v-if="pending" class="placeholder-badge">
        Coming Soon™
      </div>
    </div>

    <!-- Optional footer text -->
    <div v-if="footer" class="meme-footer">
      {{ footer }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'meme', // meme, gif, cartoon, chart, diagram
    validator: (value) => ['meme', 'gif', 'cartoon', 'chart', 'diagram', 'qr'].includes(value)
  },
  src: {
    type: String,
    default: null
  },
  alt: {
    type: String,
    default: ''
  },
  title: {
    type: String,
    default: ''
  },
  description: {
    type: String,
    default: ''
  },
  caption: {
    type: String,
    default: ''
  },
  footer: {
    type: String,
    default: ''
  },
  animated: {
    type: Boolean,
    default: false
  },
  pending: {
    type: Boolean,
    default: true
  },
  width: {
    type: String,
    default: 'auto'
  },
  height: {
    type: String,
    default: 'auto'
  }
})

const loaded = ref(false)
const error = ref(false)

const onLoad = () => {
  loaded.value = true
  error.value = false
}

const onError = () => {
  loaded.value = false
  error.value = true
}

const getIcon = () => {
  const icons = {
    meme: '🎭',
    gif: '🎬',
    cartoon: '🎨',
    chart: '📊',
    diagram: '📐',
    qr: '📱'
  }
  return icons[props.type] || '📌'
}

const getDefaultTitle = () => {
  const titles = {
    meme: '[MEME PLACEHOLDER]',
    gif: '[GIF PLACEHOLDER]',
    cartoon: '[CARTOON PLACEHOLDER]',
    chart: '[CHART PLACEHOLDER]',
    diagram: '[DIAGRAM PLACEHOLDER]',
    qr: '[QR CODE]'
  }
  return titles[props.type] || '[PLACEHOLDER]'
}
</script>

<style scoped>
.meme-slot {
  margin: 2rem auto;
  max-width: 600px;
  border-radius: 12px;
  overflow: hidden;
  position: relative;
  background: rgba(30, 41, 59, 0.3);
  border: 2px dashed rgba(148, 163, 184, 0.3);
  transition: all 0.3s ease;
}

.meme-slot--loaded {
  border-style: solid;
  background: transparent;
}

.meme-slot--animated {
  animation: pulse 2s infinite;
}

.meme-content {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

.meme-content img {
  max-width: 100%;
  height: auto;
  display: block;
  border-radius: 8px;
}

.meme-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 3rem;
  color: #94a3b8;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(148, 163, 184, 0.2);
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.meme-error {
  padding: 3rem;
  color: #ef4444;
  text-align: center;
}

.meme-placeholder {
  padding: 3rem 2rem;
  text-align: center;
  position: relative;
  min-height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.placeholder-icon {
  font-size: 3rem;
  opacity: 0.6;
}

.placeholder-text {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.placeholder-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #e2e8f0;
}

.placeholder-description {
  font-size: 1rem;
  color: #94a3b8;
  line-height: 1.5;
}

.placeholder-caption {
  font-size: 0.875rem;
  color: #64748b;
  font-style: italic;
  margin-top: 0.5rem;
}

.placeholder-badge {
  position: absolute;
  top: 1rem;
  right: 1rem;
  padding: 0.25rem 0.75rem;
  background: rgba(59, 130, 246, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.4);
  border-radius: 9999px;
  font-size: 0.75rem;
  color: #60a5fa;
  font-weight: 600;
}

.meme-footer {
  padding: 0.75rem 1rem;
  background: rgba(0, 0, 0, 0.2);
  border-top: 1px solid rgba(148, 163, 184, 0.1);
  text-align: center;
  font-size: 0.875rem;
  color: #94a3b8;
}

/* Type-specific styles */
.meme-slot--gif {
  background: repeating-linear-gradient(
    45deg,
    transparent,
    transparent 10px,
    rgba(148, 163, 184, 0.05) 10px,
    rgba(148, 163, 184, 0.05) 20px
  );
}

.meme-slot--cartoon {
  border-style: solid;
  border-width: 3px;
  box-shadow: 4px 4px 0 rgba(0, 0, 0, 0.3);
}

.meme-slot--qr {
  max-width: 300px;
  aspect-ratio: 1;
  background: white;
  border-color: #1e293b;
}

.meme-slot--qr .placeholder-text {
  color: #1e293b;
}

.meme-slot--chart,
.meme-slot--diagram {
  max-width: 800px;
  background: rgba(30, 41, 59, 0.5);
  border-color: rgba(59, 130, 246, 0.3);
}

/* Animations */
@keyframes pulse {
  0%, 100% {
    opacity: 0.8;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.02);
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Hover effects */
.meme-slot:hover {
  border-color: rgba(148, 163, 184, 0.5);
  background: rgba(30, 41, 59, 0.4);
}

.meme-slot--loaded:hover {
  transform: scale(1.02);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
}

/* Responsive */
@media (max-width: 640px) {
  .meme-slot {
    max-width: 100%;
    margin: 1rem 0;
  }

  .meme-placeholder {
    padding: 2rem 1rem;
  }

  .placeholder-icon {
    font-size: 2rem;
  }

  .placeholder-title {
    font-size: 1rem;
  }
}
</style>
