<template>
  <div class="terminal-demo">
    <div class="terminal-header">
      <div class="terminal-dots">
        <span class="dot dot-red"></span>
        <span class="dot dot-yellow"></span>
        <span class="dot dot-green"></span>
      </div>
      <span class="terminal-title">{{ title || "Terminal" }}</span>
      <button
        v-if="!autoRun"
        class="run-button"
        @click="runCommands"
        :disabled="isRunning"
      >
        {{ isRunning ? "Running..." : "Run" }}
      </button>
    </div>
    <div class="terminal-body" ref="terminalBody">
      <div
        v-for="(line, index) in displayLines"
        :key="index"
        class="terminal-line"
      >
        <template v-if="line.type === 'command'">
          <span class="terminal-prompt">{{ prompt }}</span>
          <span class="terminal-command">{{ line.text }}</span>
          <span v-if="line.showCursor" class="terminal-cursor">█</span>
        </template>
        <template v-else-if="line.type === 'output'">
          <div class="terminal-output">{{ line.text }}</div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from "vue";

const props = defineProps({
  title: {
    type: String,
    default: "Terminal",
  },
  commands: {
    type: Array,
    default: () => [],
  },
  prompt: {
    type: String,
    default: "$",
  },
  typingSpeed: {
    type: Number,
    default: 30,
  },
  autoRun: {
    type: Boolean,
    default: false,
  },
  startDelay: {
    type: Number,
    default: 500,
  },
});

const displayLines = ref([]);
const isRunning = ref(false);
const terminalBody = ref(null);

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const scrollToBottom = async () => {
  await nextTick();
  if (terminalBody.value) {
    terminalBody.value.scrollTop = terminalBody.value.scrollHeight;
  }
};

const typeCommand = async (command) => {
  const lineIndex = displayLines.value.length;
  displayLines.value.push({
    type: "command",
    text: "",
    showCursor: true,
  });

  // Type out the command character by character
  for (let i = 0; i <= command.length; i++) {
    displayLines.value[lineIndex].text = command.substring(0, i);
    await scrollToBottom();
    await sleep(props.typingSpeed);
  }

  // Remove cursor after typing
  displayLines.value[lineIndex].showCursor = false;
};

const showOutput = async (output, delay = 100) => {
  await sleep(delay);

  // Split output by newlines and add each line
  const lines = output.split("\n");
  for (const line of lines) {
    displayLines.value.push({
      type: "output",
      text: line,
    });
    await scrollToBottom();
    await sleep(50); // Small delay between output lines
  }
};

const runCommands = async () => {
  if (isRunning.value) return;

  isRunning.value = true;
  displayLines.value = [];

  for (const command of props.commands) {
    // Type the command
    await typeCommand(command.cmd);

    // Show the output
    if (command.output) {
      const outputDelay = command.delay || 100;
      await showOutput(command.output, outputDelay);
    }

    // Add a small pause between commands
    await sleep(300);
  }

  isRunning.value = false;
};

onMounted(() => {
  if (props.autoRun) {
    setTimeout(() => {
      runCommands();
    }, props.startDelay);
  }
});
</script>

<style scoped>
.terminal-demo {
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
  border-radius: 8px;
  overflow: hidden;
  background: #1e1e1e;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow:
    0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.terminal-header {
  display: flex;
  align-items: center;
  padding: 10px 15px;
  background: #2d2d2d;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.terminal-dots {
  display: flex;
  gap: 8px;
  margin-right: auto;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.dot-red {
  background: #ff5f56;
}

.dot-yellow {
  background: #ffbd2e;
}

.dot-green {
  background: #27c93f;
}

.terminal-title {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  color: #888;
  font-size: 13px;
  font-weight: 500;
}

.run-button {
  margin-left: auto;
  padding: 4px 12px;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 4px;
  color: #60a5fa;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.run-button:hover:not(:disabled) {
  background: rgba(59, 130, 246, 0.2);
  border-color: rgba(59, 130, 246, 0.5);
}

.run-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.terminal-body {
  padding: 15px;
  font-family:
    "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Consolas, "Courier New",
    monospace;
  font-size: 14px;
  line-height: 1.6;
  color: #d4d4d4;
  height: 400px;
  max-height: 60vh;
  overflow-y: auto;
  overflow-x: hidden;
}

.terminal-body::-webkit-scrollbar {
  width: 8px;
}

.terminal-body::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
}

.terminal-body::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
}

.terminal-body::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

.terminal-line {
  margin-bottom: 2px;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.terminal-prompt {
  color: #27c93f;
  margin-right: 8px;
  font-weight: 600;
}

.terminal-command {
  color: #f1f1f1;
}

.terminal-cursor {
  display: inline-block;
  width: 8px;
  height: 16px;
  background: #27c93f;
  animation: blink 1s step-end infinite;
  margin-left: 2px;
  vertical-align: text-bottom;
}

.terminal-output {
  color: #a8a8a8;
  margin-left: 20px;
  white-space: pre-wrap;
  line-height: 1.4;
}

@keyframes blink {
  0%,
  50% {
    opacity: 1;
  }
  51%,
  100% {
    opacity: 0;
  }
}

/* Dark mode optimizations */
@media (prefers-color-scheme: dark) {
  .terminal-demo {
    background: #0d0d0d;
  }

  .terminal-header {
    background: #1a1a1a;
  }
}
</style>
