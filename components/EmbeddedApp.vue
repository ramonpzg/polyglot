<template>
  <div class="embedded-app-container">
    <div class="app-header">
      <div class="app-info">
        <div class="app-status">
          <span class="status-dot" :class="{ active: isLoaded }"></span>
          <span class="app-title">{{ title }}</span>
        </div>
        <span v-if="subtitle" class="app-subtitle">{{ subtitle }}</span>
      </div>
      <div class="app-controls">
        <button
          v-if="showRefresh"
          @click="refreshApp"
          class="control-button"
          title="Refresh"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path
              d="M23 4v6h-6M1 20v-6h6M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"
            />
          </svg>
        </button>
        <button
          v-if="showFullscreen"
          @click="toggleFullscreen"
          class="control-button"
          title="Fullscreen"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path
              d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"
            />
          </svg>
        </button>
        <a
          v-if="src"
          :href="src"
          target="_blank"
          class="control-button external-link"
          title="Open in new tab"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path
              d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14L21 3"
            />
          </svg>
        </a>
      </div>
    </div>

    <div class="app-body" :style="{ height: computedHeight }">
      <!-- Loading state -->
      <div v-if="isLoading" class="loading-state">
        <div class="loading-spinner"></div>
        <span class="loading-text">Loading {{ title }}...</span>
      </div>

      <!-- Error state -->
      <div v-else-if="hasError" class="error-state">
        <svg
          width="48"
          height="48"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
        <span class="error-text">Failed to load application</span>
        <button @click="retryLoad" class="retry-button">Try Again</button>
      </div>

      <!-- Placeholder when no src -->
      <div v-else-if="!src" class="placeholder-state">
        <svg
          width="48"
          height="48"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
          <line x1="9" y1="9" x2="15" y2="15" />
          <line x1="15" y1="9" x2="9" y2="15" />
        </svg>
        <span class="placeholder-text">No application URL provided</span>
      </div>

      <!-- Iframe -->
      <iframe
        v-else
        ref="iframeRef"
        class="app-iframe"
        :src="iframeSrc"
        :title="title"
        @load="handleLoad"
        @error="handleError"
        :sandbox="sandbox"
        :allow="allow"
      />
    </div>

    <!-- Optional footer -->
    <div v-if="showFooter && footerText" class="app-footer">
      <span class="footer-text">{{ footerText }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";

const props = defineProps({
  src: {
    type: String,
    default: "",
  },
  title: {
    type: String,
    default: "Embedded Application",
  },
  subtitle: {
    type: String,
    default: "",
  },
  height: {
    type: [Number, String],
    default: 500,
  },
  showRefresh: {
    type: Boolean,
    default: true,
  },
  showFullscreen: {
    type: Boolean,
    default: true,
  },
  showFooter: {
    type: Boolean,
    default: false,
  },
  footerText: {
    type: String,
    default: "",
  },
  sandbox: {
    type: String,
    default: "allow-scripts allow-same-origin allow-forms allow-popups",
  },
  allow: {
    type: String,
    default: "accelerometer; camera; microphone; geolocation",
  },
  autoReload: {
    type: Number,
    default: 0, // Auto reload interval in seconds, 0 = disabled
  },
});

const iframeRef = ref(null);
const iframeSrc = ref(props.src);
const isLoading = ref(true);
const isLoaded = ref(false);
const hasError = ref(false);
const isFullscreen = ref(false);
let reloadInterval = null;

const computedHeight = computed(() => {
  const h = props.height;
  return typeof h === "number" ? `${h}px` : h;
});

const refreshApp = () => {
  if (!props.src) return;
  isLoading.value = true;
  isLoaded.value = false;
  hasError.value = false;
  // Force reload by changing src
  iframeSrc.value = "";
  setTimeout(() => {
    iframeSrc.value = props.src;
  }, 10);
};

const retryLoad = () => {
  hasError.value = false;
  isLoading.value = true;
  refreshApp();
};

const handleLoad = () => {
  isLoading.value = false;
  isLoaded.value = true;
  hasError.value = false;
};

const handleError = () => {
  isLoading.value = false;
  isLoaded.value = false;
  hasError.value = true;
};

const toggleFullscreen = () => {
  if (!iframeRef.value) return;

  if (!isFullscreen.value) {
    if (iframeRef.value.requestFullscreen) {
      iframeRef.value.requestFullscreen();
    } else if (iframeRef.value.webkitRequestFullscreen) {
      iframeRef.value.webkitRequestFullscreen();
    } else if (iframeRef.value.mozRequestFullScreen) {
      iframeRef.value.mozRequestFullScreen();
    }
    isFullscreen.value = true;
  } else {
    if (document.exitFullscreen) {
      document.exitFullscreen();
    } else if (document.webkitExitFullscreen) {
      document.webkitExitFullscreen();
    } else if (document.mozCancelFullScreen) {
      document.mozCancelFullScreen();
    }
    isFullscreen.value = false;
  }
};

const setupAutoReload = () => {
  if (props.autoReload > 0) {
    reloadInterval = setInterval(() => {
      refreshApp();
    }, props.autoReload * 1000);
  }
};

onMounted(() => {
  setupAutoReload();

  // Handle fullscreen change events
  const handleFullscreenChange = () => {
    isFullscreen.value = !!document.fullscreenElement;
  };

  document.addEventListener("fullscreenchange", handleFullscreenChange);
  document.addEventListener("webkitfullscreenchange", handleFullscreenChange);
  document.addEventListener("mozfullscreenchange", handleFullscreenChange);

  // Initialize loading state
  if (props.src) {
    isLoading.value = true;
  } else {
    isLoading.value = false;
  }
});

onUnmounted(() => {
  if (reloadInterval) {
    clearInterval(reloadInterval);
  }
});
</script>

<style scoped>
.embedded-app-container {
  width: 100%;
  background: #1a1a1a;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
  box-shadow:
    0 10px 40px rgba(0, 0, 0, 0.4),
    0 2px 10px rgba(0, 0, 0, 0.2);
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: linear-gradient(180deg, #2a2a2a 0%, #222222 100%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.app-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.app-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #dc2626;
  transition: background 0.3s ease;
}

.status-dot.active {
  background: #10b981;
  animation: pulse 2s infinite;
}

.app-title {
  font-size: 14px;
  font-weight: 600;
  color: #e5e7eb;
}

.app-subtitle {
  font-size: 12px;
  color: #9ca3af;
}

.app-controls {
  display: flex;
  gap: 8px;
}

.control-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: #9ca3af;
  cursor: pointer;
  transition: all 0.2s ease;
}

.control-button:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #e5e7eb;
  transform: translateY(-1px);
}

.external-link {
  text-decoration: none;
}

.app-body {
  position: relative;
  width: 100%;
  background: #0d0d0d;
  min-height: 200px;
}

.app-iframe {
  width: 100%;
  height: 100%;
  border: none;
  display: block;
}

/* Loading state */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 16px;
  color: #9ca3af;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-text {
  font-size: 14px;
}

/* Error state */
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 16px;
  color: #ef4444;
}

.error-text {
  font-size: 14px;
  color: #f87171;
}

.retry-button {
  padding: 8px 16px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 6px;
  color: #f87171;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.retry-button:hover {
  background: rgba(239, 68, 68, 0.2);
}

/* Placeholder state */
.placeholder-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 16px;
  color: #6b7280;
}

.placeholder-text {
  font-size: 14px;
}

/* Footer */
.app-footer {
  padding: 8px 16px;
  background: #1a1a1a;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.footer-text {
  font-size: 12px;
  color: #6b7280;
}

/* Animations */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .app-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .app-controls {
    align-self: flex-end;
  }
}
</style>
