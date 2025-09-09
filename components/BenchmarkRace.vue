<template>
  <div class="race">
    <div class="header">
      <span>Performance Reality Check</span>
      <div class="actions">
        <button class="btn" @click="run">Run</button>
        <button class="btn" @click="shuffle">Re-run</button>
      </div>
    </div>
    <div v-for="row in rows" :key="row.name" class="barrow">
      <span class="name">{{ row.name }}</span>
      <div class="bar">
        <div class="fill" :style="{ width: row.width + '%' }"></div>
      </div>
      <span class="val">{{ row.value.toFixed(2) }}s</span>
    </div>
    <div class="hint">Shorter is better. Yes, we know.</div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  results: { type: Object, default: () => ({ Python: 30.0, 'C++23': 0.30, Zig: 0.28, Rust: 0.32 }) },
})

const rows = ref([])
const toRows = (obj) => Object.entries(obj).map(([name, v]) => ({ name, value: Number(v), width: 0 }))
let timer

const run = () => {
  clearInterval(timer)
  const base = Math.max(...rows.value.map(r => r.value)) || 1
  const target = rows.value.map(r => ({ name: r.name, value: r.value, width: (r.value / base) * 100 }))
  rows.value.forEach(r => (r.width = 0))
  let t = 0
  timer = setInterval(() => {
    t += 5
    rows.value.forEach((r, i) => {
      const tw = target[i].width
      r.width = Math.min(tw, r.width + Math.max(1, tw / 20))
    })
    if (rows.value.every((r, i) => r.width >= target[i].width)) clearInterval(timer)
  }, 40)
}

const shuffle = () => {
  // jitter +/- 7%
  rows.value.forEach(r => { r.value = r.value * (0.93 + Math.random() * 0.14) })
  run()
}

rows.value = toRows(props.results)
</script>

<style scoped>
.race { width: 100%; max-width: 980px; margin: 0 auto; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.actions { display: flex; gap: 8px; }
.btn { padding: 6px 10px; border: 1px solid #4445; background: #1118; color: #ddd; border-radius: 6px; }
.barrow { display: grid; grid-template-columns: 120px 1fr 90px; gap: 10px; align-items: center; margin: 8px 0; }
.name { font-weight: 600; }
.bar { background: #222; border-radius: 8px; overflow: hidden; height: 16px; }
.fill { height: 100%; background: linear-gradient(90deg, #2b90b6, #4ec5d4); transition: width .2s ease; }
.val { font-variant-numeric: tabular-nums; text-align: right; }
.hint { margin-top: 8px; font-size: 12px; opacity: .7; }
</style>

