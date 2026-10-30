<script setup lang="ts">
import { message } from 'ant-design-vue'
import dayjs, { type Dayjs } from 'dayjs'
import type { DetectionResult, SensorReading } from '~/composables/useApi'
import { buildFlowTraces, buildPressureTraces, plotLayoutBase } from '~/composables/usePlotly'

const api = useApi()
const range = ref<[Dayjs, Dayjs]>([dayjs().subtract(30, 'minute'), dayjs()])
const readings = ref<SensorReading[]>([])
const detections = ref<DetectionResult[]>([])
const loading = ref(false)

const flowTraces = computed(() => buildFlowTraces(readings.value))
const pressureTraces = computed(() => buildPressureTraces(readings.value))
const flowLayout = { ...plotLayoutBase, yaxis: { title: '流量 (m³/h)' } }
const pressureLayout = { ...plotLayoutBase, yaxis: { title: '壓力 (MPa)' } }

const columns = [
  { title: '時間', dataIndex: 'ts', key: 'ts' },
  { title: '方法', dataIndex: 'method', key: 'method' },
  { title: '嚴重度', dataIndex: 'severity', key: 'severity' },
  { title: '可疑', dataIndex: 'leak_suspected', key: 'leak_suspected' },
]

function methodLabel(method: string) {
  const map: Record<string, string> = {
    pressure_gradient: '壓力梯度法',
    flow_imbalance: '流量變化量',
    pressure_wave: '壓力波',
  }
  return map[method] || method
}

const tableData = computed(() =>
  detections.value.map((d) => ({
    ...d,
    method: methodLabel(d.method),
    leak_suspected: d.leak_suspected ? '是' : '否',
  })),
)

async function query() {
  if (!range.value?.[0] || !range.value?.[1]) {
    message.warning('請選擇時間區間')
    return
  }
  loading.value = true
  const from = range.value[0].toISOString()
  const to = range.value[1].toISOString()
  try {
    const [r, d] = await Promise.all([api.getReadings(from, to), api.getDetections(from, to)])
    readings.value = r
    detections.value = d
    if (!r.length) {
      message.info('此區間尚無讀數資料')
    }
  } catch (err) {
    console.error(err)
    message.error('歷史查詢失敗，請確認後端是否啟動')
  } finally {
    loading.value = false
  }
}

onMounted(query)
</script>

<template>
  <div class="page">
    <div class="page-head">
      <h1>歷史查詢</h1>
      <p>依時間區間檢視流量／壓力趨勢與偵測紀錄</p>
    </div>

    <div class="panel toolbar">
      <a-range-picker
        v-model:value="range"
        show-time
        format="YYYY-MM-DD HH:mm:ss"
        style="max-width: 420px"
      />
      <a-button type="primary" :loading="loading" @click="query">查詢</a-button>
    </div>

    <a-row :gutter="[16, 16]" style="margin-top: 16px">
      <a-col :xs="24" :lg="12">
        <div class="panel">
          <PlotlyChart title="流量趨勢" :traces="flowTraces" :layout="flowLayout" />
        </div>
      </a-col>
      <a-col :xs="24" :lg="12">
        <div class="panel">
          <PlotlyChart title="壓力趨勢" :traces="pressureTraces" :layout="pressureLayout" />
        </div>
      </a-col>
    </a-row>

    <div class="panel" style="margin-top: 16px">
      <h3>偵測紀錄</h3>
      <a-table
        :columns="columns"
        :data-source="tableData"
        :loading="loading"
        row-key="id"
        size="middle"
        :pagination="{ pageSize: 10 }"
      />
    </div>
  </div>
</template>

<style scoped>
.page-head h1 {
  margin: 0 0 4px;
  font-size: 28px;
  color: #0b3d2e;
}

.page-head p {
  margin: 0 0 20px;
  color: #4d6359;
}

.panel {
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(11, 61, 46, 0.08);
  border-radius: 8px;
  padding: 16px;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.panel h3 {
  margin: 0 0 12px;
  color: #0b3d2e;
}
</style>
