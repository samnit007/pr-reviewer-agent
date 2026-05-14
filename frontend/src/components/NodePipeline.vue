<template>
  <div class="flex items-center gap-1 flex-wrap">
    <template v-for="(node, i) in nodes" :key="node.id">
      <div class="flex items-center gap-1">
        <div :class="[
          'px-2 py-1 rounded text-xs font-mono font-medium transition-all',
          visited.includes(node.id)
            ? 'bg-indigo-100 text-indigo-700'
            : running && i === nextIdx
              ? 'bg-amber-100 text-amber-700 animate-pulse'
              : 'bg-gray-100 text-gray-400'
        ]">
          {{ node.label }}
        </div>
        <span v-if="i < nodes.length - 1" class="text-gray-300 text-xs">→</span>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  visited: string[]
  running: boolean
  isLarge: boolean
}>()

const nodes = computed(() => props.isLarge
  ? [
      { id: 'fetch_pr', label: 'fetch' },
      { id: 'analyse_size', label: 'size' },
      { id: 'summarise_only', label: 'summarise' },
      { id: 'draft_review', label: 'draft' },
    ]
  : [
      { id: 'fetch_pr', label: 'fetch' },
      { id: 'analyse_size', label: 'size' },
      { id: 'check_style', label: 'style' },
      { id: 'check_logic', label: 'logic' },
      { id: 'check_tests', label: 'tests' },
      { id: 'draft_review', label: 'draft' },
    ]
)

const nextIdx = computed(() => {
  const ids = nodes.value.map(n => n.id)
  const lastVisited = [...props.visited].reverse().find(v => ids.includes(v))
  if (!lastVisited) return 0
  return ids.indexOf(lastVisited) + 1
})
</script>
