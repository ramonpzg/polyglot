<template>
  <div class="particles-container">
    <div
      v-for="(particle, index) in particles"
      :key="index"
      class="particle"
      :style="{
        left: `${particle.x}%`,
        top: `${particle.y}%`,
        animationDelay: `${particle.delay}s`,
        opacity: particle.opacity,
        fontSize: `${particle.size}px`,
      }"
    >
      {{ particle.code }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";

const particles = ref([]);

const codeSnippets = [
  "def hello():",
  'print("Hello")',
  "import numpy as np",
  "for i in range(10):",
  'if __name__ == "__main__":',
  "from fastapi import FastAPI",
  "app = FastAPI()",
  '@app.get("/")',
  "async def root():",
  'return {"message": "Hello World"}',
  "import torch",
  "model = torch.nn.Linear(10, 2)",
  "import pandas as pd",
  "df = pd.DataFrame()",
  "plt.plot(x, y)",
  "import asyncio",
  "await asyncio.sleep(1)",
  "from typing import List",
  "def add(a: int, b: int) -> int:",
  "return a + b",
  "class MyClass:",
  "def __init__(self):",
  "self.value = 42",
  "def __str__(self):",
  'return f"MyClass({self.value})"',
];

onMounted(() => {
  // Generate 50 particles
  const newParticles = [];
  for (let i = 0; i < 50; i++) {
    newParticles.push({
      x: Math.random() * 100,
      y: Math.random() * 100,
      delay: Math.random() * 5,
      size: Math.random() * 10 + 10, // between 10 and 20px
      opacity: Math.random() * 0.5 + 0.1, // between 0.1 and 0.6
      code: codeSnippets[Math.floor(Math.random() * codeSnippets.length)],
    });
  }
  particles.value = newParticles;
});
</script>

<style scoped>
.particles-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: -1; /* behind the content */
}

.particle {
  position: absolute;
  color: rgba(100, 200, 255, 0.7);
  font-family: "Fira Code", monospace;
  white-space: nowrap;
  animation: float 15s infinite linear;
  pointer-events: none; /* so they don't block interaction */
}

@keyframes float {
  0% {
    transform: translateY(0) translateX(0) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 0.7;
  }
  90% {
    opacity: 0.7;
  }
  100% {
    transform: translateY(-100vh) translateX(100px) rotate(360deg);
    opacity: 0;
  }
}
</style>
