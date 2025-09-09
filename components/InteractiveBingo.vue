<template>
  <div class="bingo">
    <div class="header">
      <span>Python Performance Bingo</span>
      <button class="reset" @click="reset">Reset</button>
    </div>
    <div class="grid">
      <button
        v-for="(sq, i) in board"
        :key="i"
        class="cell"
        :class="{ on: sq.on }"
        @click="toggle(i)"
      >
        {{ sq.text }}
      </button>
    </div>
    <div v-if="hasBingo" class="bingo-banner">Bingo. Fancy that.</div>
  </div>
  
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  squares: { type: Array, default: () => [] },
})

const defaults = [
  'Python is slow',
  'Just rewrite in Rust',
  'Use NumPy',
  'GIL problems',
  "Threading won't help",
  'Micro-optimise loops',
  'Pandas solves it',
  'Use pypy',
  'Cache it',
  'Profile first',
  'Numba? Maybe',
  'It’s the disk',
  'GPU it',
  'Moar cores',
  'Async fixes all',
  'Rewrite everything',
  'SIMD magic',
  'Batch it',
  'WASM?',
  'SQL does it better',
  'Kill the GIL',
  'CPython 3.13 FTW',
  'Try Polars',
  'UDFs are bad',
  'It depends',
]

const board = ref([])

const seedBoard = () => {
  const items = (props.squares?.length ? props.squares : defaults).slice(0, 25)
  while (items.length < 25) items.push('')
  board.value = items.map(t => ({ text: t, on: false }))
}

const toggle = (i) => {
  board.value[i].on = !board.value[i].on
}

const reset = () => seedBoard()

const hasBingo = computed(() => {
  const b = board.value
  if (b.length < 25) return false
  const on = (i) => b[i].on
  const lines = []
  // rows
  for (let r=0; r<5; r++) lines.push([0,1,2,3,4].map(c => r*5 + c))
  // cols
  for (let c=0; c<5; c++) lines.push([0,1,2,3,4].map(r => r*5 + c))
  // diagonals
  lines.push([0,6,12,18,24])
  lines.push([4,8,12,16,20])
  return lines.some(line => line.every(on))
})

watch(() => props.squares, seedBoard, { immediate: true })
</script>

<style scoped>
.bingo { width: 100%; max-width: 980px; margin: 0 auto; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.reset { font-size: 12px; padding: 6px 10px; border: 1px solid var(--slidev-theme-primary, #2b90b6); border-radius: 6px; }
.grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; }
.cell { min-height: 70px; border: 1px solid #4445; background: #1118; color: #ddd; border-radius: 8px; padding: 8px; text-align: center; transition: background .2s, transform .05s; }
.cell:hover { transform: translateY(-1px); }
.cell.on { background: #2b90b6; color: white; border-color: #2b90b6; }
.bingo-banner { margin-top: 10px; padding: 8px 12px; background: #1a3f4a; color: #d9f2ff; display: inline-block; border-radius: 8px; }
</style>

