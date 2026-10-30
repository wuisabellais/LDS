<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps<{
  traces: unknown[]
  layout?: Record<string, unknown>
  title?: string
}>()

const el = ref<HTMLDivElement | null>(null)
let Plotly: typeof import('plotly.js-dist-min') | null = null

async function render() {
  if (!el.value) return
  if (!Plotly) {
    Plotly = await import('plotly.js-dist-min')
  }
  const layout = {
    title: props.title || '',
    ...props.layout,
  }
  await Plotly.newPlot(el.value, props.traces as never, layout as never, {
    responsive: true,
    displayModeBar: false,
  })
}

onMounted(render)
watch(() => [props.traces, props.layout, props.title], render, { deep: true })

onBeforeUnmount(() => {
  if (el.value && Plotly) {
    Plotly.purge(el.value)
  }
})
</script>

<template>
  <div ref="el" class="plotly-chart" />
</template>

<style scoped>
.plotly-chart {
  width: 100%;
  min-height: 320px;
}
</style>
