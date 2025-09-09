<template>
  <div class="live-poll-container">
    <div class="poll-header">
      <h3 class="poll-title">{{ title || "Live Audience Poll" }}</h3>
      <div class="poll-status">
        <span
          class="status-indicator"
          :class="{ connected: isConnected }"
        ></span>
        <span class="status-text">{{ statusText }}</span>
      </div>
    </div>

    <div class="poll-options">
      <div
        v-for="(option, index) in pollOptions"
        :key="index"
        class="poll-option"
        @click="vote(index)"
        :class="{ voted: votedIndex === index, winner: isWinner(index) }"
      >
        <div class="option-content">
          <span class="option-text">{{ option.text }}</span>
          <span class="option-votes">{{ option.votes }} votes</span>
        </div>
        <div class="option-bar-container">
          <div
            class="option-bar"
            :style="{ width: getPercentage(option.votes) + '%' }"
          ></div>
        </div>
        <div class="option-percentage">{{ getPercentage(option.votes) }}%</div>
      </div>
    </div>

    <div class="poll-footer">
      <div class="total-votes">
        <span class="total-label">Total votes:</span>
        <span class="total-count">{{ totalVotes }}</span>
      </div>
      <button v-if="showReset" @click="resetPoll" class="reset-button">
        Reset Poll
      </button>
    </div>

    <!-- Floating vote animations -->
    <transition-group name="vote-float" tag="div">
      <div
        v-for="vote in floatingVotes"
        :key="vote.id"
        class="floating-vote"
        :style="{
          left: vote.x + 'px',
          top: vote.y + 'px',
          '--color': vote.color,
        }"
      >
        +1
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";

const props = defineProps({
  options: {
    type: Array,
    default: () => [
      "Python is slow",
      "Just use NumPy",
      "Rewrite in Rust",
      "It depends",
    ],
  },
  title: {
    type: String,
    default: "",
  },
  showReset: {
    type: Boolean,
    default: false,
  },
  mockMode: {
    type: Boolean,
    default: true,
  },
});

// Reactive state
const pollOptions = ref([]);
const votedIndex = ref(null);
const isConnected = ref(false);
const floatingVotes = ref([]);
let voteIdCounter = 0;
let mockInterval = null;

// Initialize poll options
const initializePoll = () => {
  pollOptions.value = props.options.map((text) => ({
    text,
    votes: Math.floor(Math.random() * 10) + 1, // Start with some random votes
  }));
};

// Computed properties
const totalVotes = computed(() => {
  return pollOptions.value.reduce((sum, option) => sum + option.votes, 0);
});

const statusText = computed(() => {
  return isConnected.value ? "Live" : "Connecting...";
});

// Get percentage for an option
const getPercentage = (votes) => {
  if (totalVotes.value === 0) return 0;
  return Math.round((votes / totalVotes.value) * 100);
};

// Check if option is the winner
const isWinner = (index) => {
  if (totalVotes.value === 0) return false;
  const maxVotes = Math.max(...pollOptions.value.map((o) => o.votes));
  return pollOptions.value[index].votes === maxVotes && maxVotes > 0;
};

// Vote for an option
const vote = (index) => {
  if (votedIndex.value !== null) return; // Already voted

  votedIndex.value = index;
  pollOptions.value[index].votes++;

  // Add floating animation
  addFloatingVote(index);

  // Simulate other votes coming in after user votes
  if (props.mockMode) {
    setTimeout(() => {
      simulateOtherVotes();
    }, 500);
  }
};

// Add floating vote animation
const addFloatingVote = (optionIndex) => {
  const id = voteIdCounter++;
  const colors = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"];

  floatingVotes.value.push({
    id,
    x: Math.random() * 300 + 50,
    y: 100 + optionIndex * 80,
    color: colors[optionIndex % colors.length],
  });

  // Remove after animation
  setTimeout(() => {
    floatingVotes.value = floatingVotes.value.filter((v) => v.id !== id);
  }, 2000);
};

// Simulate other people voting
const simulateOtherVotes = () => {
  const voteCount = Math.floor(Math.random() * 5) + 3;
  let votesAdded = 0;

  const addVote = () => {
    if (votesAdded >= voteCount) return;

    const randomIndex = Math.floor(Math.random() * pollOptions.value.length);
    pollOptions.value[randomIndex].votes++;
    addFloatingVote(randomIndex);
    votesAdded++;

    setTimeout(addVote, Math.random() * 300 + 100);
  };

  addVote();
};

// Reset the poll
const resetPoll = () => {
  votedIndex.value = null;
  initializePoll();
};

// Mock real-time updates
const startMockUpdates = () => {
  if (!props.mockMode) return;

  mockInterval = setInterval(() => {
    // Randomly add votes to simulate real-time activity
    if (Math.random() > 0.7 && votedIndex.value !== null) {
      const randomIndex = Math.floor(Math.random() * pollOptions.value.length);
      pollOptions.value[randomIndex].votes++;
      addFloatingVote(randomIndex);
    }
  }, 3000);
};

// Lifecycle hooks
onMounted(() => {
  initializePoll();

  // Simulate connection
  setTimeout(() => {
    isConnected.value = true;
  }, 1000);

  // Start mock updates if in mock mode
  startMockUpdates();
});

onUnmounted(() => {
  if (mockInterval) {
    clearInterval(mockInterval);
  }
});
</script>

<style scoped>
.live-poll-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background: linear-gradient(
    135deg,
    rgba(30, 41, 59, 0.5),
    rgba(15, 23, 42, 0.5)
  );
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.1);
  position: relative;
  overflow: hidden;
}

.poll-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.poll-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #e2e8f0;
  margin: 0;
}

.poll-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ef4444;
  animation: pulse 2s infinite;
}

.status-indicator.connected {
  background: #10b981;
}

.status-text {
  font-size: 0.875rem;
  color: #94a3b8;
}

.poll-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}

.poll-option {
  background: rgba(30, 41, 59, 0.3);
  border: 1px solid rgba(148, 163, 184, 0.1);
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.poll-option:hover {
  background: rgba(30, 41, 59, 0.5);
  border-color: rgba(148, 163, 184, 0.2);
  transform: translateX(4px);
}

.poll-option.voted {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.3);
}

.poll-option.winner {
  border-color: rgba(16, 185, 129, 0.5);
  box-shadow: 0 0 20px rgba(16, 185, 129, 0.2);
}

.option-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.option-text {
  font-size: 1rem;
  color: #e2e8f0;
}

.option-votes {
  font-size: 0.875rem;
  color: #94a3b8;
}

.option-bar-container {
  height: 6px;
  background: rgba(148, 163, 184, 0.1);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 4px;
}

.option-bar {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6);
  border-radius: 3px;
  transition: width 0.5s ease;
}

.poll-option.winner .option-bar {
  background: linear-gradient(90deg, #10b981, #34d399);
}

.option-percentage {
  font-size: 0.75rem;
  color: #64748b;
  text-align: right;
}

.poll-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid rgba(148, 163, 184, 0.1);
}

.total-votes {
  display: flex;
  gap: 8px;
  align-items: center;
}

.total-label {
  font-size: 0.875rem;
  color: #94a3b8;
}

.total-count {
  font-size: 1.125rem;
  font-weight: 600;
  color: #e2e8f0;
}

.reset-button {
  padding: 6px 12px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 6px;
  color: #f87171;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.reset-button:hover {
  background: rgba(239, 68, 68, 0.2);
  border-color: rgba(239, 68, 68, 0.5);
}

/* Floating vote animations */
.floating-vote {
  position: absolute;
  font-size: 1.25rem;
  font-weight: bold;
  color: var(--color);
  pointer-events: none;
  animation: floatUp 2s ease-out forwards;
  z-index: 100;
}

.vote-float-enter-active {
  transition: all 0.3s ease;
}

.vote-float-leave-active {
  transition: all 0.3s ease;
}

.vote-float-enter-from {
  opacity: 0;
  transform: scale(0.5);
}

.vote-float-leave-to {
  opacity: 0;
  transform: translateY(-50px);
}

@keyframes floatUp {
  0% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
  100% {
    opacity: 0;
    transform: translateY(-80px) scale(0.5);
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
</style>
