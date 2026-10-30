<script setup lang="ts">
import { message } from 'ant-design-vue'
import type { SensorReading, StatusResponse } from '~/composables/useApi'
import { buildFlowTraces, buildPressureTraces, plotLayoutBase } from '~/composables/usePlotly'

const api = useApi()
const status = ref<StatusResponse | null>(null)
const readings = ref<SensorReading[]>([])
const loading = ref(false)
let timer: ReturnType<typeof setInterval> | null = null

const flowTraces = computed(() => buildFlowTraces(readings.value))
const pressureTraces = computed(() => buildPressureTraces(readings.value))

const flowLayout = {
  ...plotLayoutBase,
  yaxis: { title: '流量 (m³/h)' },
}
const pressureLayout = {
  ...plotLayoutBase,
  yaxis: { title: '壓力 (MPa)' },
}

function severityColor(severity: string) {
  if (severity === 'alarm' || severity === '告警') return 'error'
  if (severity === 'watch' || severity === '觀察') return 'warning'
  return 'success'
}

function methodLabel(method: string) {
  const map: Record<string, string> = {
    pressure_gradient: '壓力梯度法',
    flow_imbalance: '流量變化量',
    pressure_wave: '壓力波',
  }
  return map[method] || method
}

async function refresh() {
  try {
    const [statusRes, readingsRes] = await Promise.all([
      api.getStatus(),
      api.getLatestReadings(90),
    ])
    status.value = statusRes
    readings.value = readingsRes
  } catch (err) {
    console.error(err)
    message.error('無法取得監測資料，請確認後端是否啟動')
  }
}

async function onLeakChange(checked: boolean) {
  loading.value = true
  try {
    await api.setLeak(checked)
    await refresh()
  } catch {
    message.error('更新洩漏注入失敗')
  } finally {
    loading.value = false
  }
}

async function onTransportChange(checked: boolean) {
  loading.value = true
  try {
    await api.setTransport(checked)
    await refresh()
  } catch {
    message.error('更新輸送狀態失敗')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await refresh()
  timer = setInterval(refresh, 2500)
})

onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <div class="page">
    <div class="page-head">
      <h1>即時監測</h1>
      <p>單管線模擬監測：輸送狀態、洩漏跡象與趨勢一覽</p>
    </div>

    <a-row :gutter="[16, 16]">
      <a-col :xs="24" :lg="16">
        <a-row :gutter="[12, 12]">
          <a-col :xs="12" :md="6">
            <a-statistic title="輸送狀態" :value="status?.transport_status || '—'" />
          </a-col>
          <a-col :xs="12" :md="6">
            <a-statistic title="監測狀態" :value="status?.monitor_status || '—'">
              <template #suffix>
                <a-tag
                  v-if="status"
                  :color="severityColor(status.monitor_status)"
                  style="margin-left: 8px"
                >
                  {{ status.monitor_status }}
                </a-tag>
              </template>
            </a-statistic>
          </a-col>
          <a-col :xs="12" :md="6">
            <a-statistic title="內容物" :value="status?.content_type || '—'" />
          </a-col>
          <a-col :xs="12" :md="6">
            <a-statistic
              title="溫度"
              :value="status?.latest?.temperature ?? '—'"
              suffix="°C"
              :precision="1"
            />
          </a-col>
          <a-col :xs="12" :md="6">
            <a-statistic
              title="入口壓力"
              :value="status?.latest?.pressure_in ?? '—'"
              suffix="MPa"
              :precision="3"
            />
          </a-col>
          <a-col :xs="12" :md="6">
            <a-statistic
              title="出口壓力"
              :value="status?.latest?.pressure_out ?? '—'"
              suffix="MPa"
              :precision="3"
            />
          </a-col>
          <a-col :xs="12" :md="6">
            <a-statistic
              title="入口流量"
              :value="status?.latest?.flow_in ?? '—'"
              suffix="m³/h"
              :precision="2"
            />
          </a-col>
          <a-col :xs="12" :md="6">
            <a-statistic
              title="出口流量"
              :value="status?.latest?.flow_out ?? '—'"
              suffix="m³/h"
              :precision="2"
            />
          </a-col>
        </a-row>
      </a-col>

      <a-col :xs="24" :lg="8">
        <div class="control-panel">
          <h3>模擬控制</h3>
          <div class="control-row">
            <span>輸送運行</span>
            <a-switch
              :checked="status?.transport_running ?? true"
              :loading="loading"
              checked-children="輸送中"
              un-checked-children="停輸"
              @change="(v: boolean) => onTransportChange(v)"
            />
          </div>
          <div class="control-row">
            <span>洩漏注入</span>
            <a-switch
              :checked="status?.leak_injected ?? false"
              :loading="loading"
              checked-children="ON"
              un-checked-children="OFF"
              @change="(v: boolean) => onLeakChange(v)"
            />
          </div>
          <a-typography-text type="secondary">
            開啟洩漏注入可驗證三種演算法與告警顯示。
          </a-typography-text>
        </div>
      </a-col>
    </a-row>

    <a-row :gutter="[16, 16]" style="margin-top: 16px">
      <a-col :xs="24" :md="12">
        <div class="panel">
          <a-statistic
            title="流量變化率"
            :value="status?.flow_change_rate ?? 0"
            suffix="m³/h·s"
            :precision="4"
          />
        </div>
      </a-col>
      <a-col :xs="24" :md="12">
        <div class="panel">
          <a-statistic
            title="壓力變化率"
            :value="status?.pressure_change_rate ?? 0"
            suffix="MPa/s"
            :precision="6"
          />
        </div>
      </a-col>
    </a-row>

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
      <h3>偵測演算法</h3>
      <a-row :gutter="[12, 12]">
        <a-col
          v-for="method in status?.methods || []"
          :key="method.method"
          :xs="24"
          :md="8"
        >
          <a-card size="small" :title="methodLabel(method.method)">
            <a-tag :color="severityColor(method.severity)">
              {{ method.severity }}
            </a-tag>
            <div class="metrics">
              <div v-for="(val, key) in method.metrics" :key="key">
                <span class="metric-key">{{ key }}</span>
                <span>{{ val }}</span>
              </div>
            </div>
          </a-card>
        </a-col>
      </a-row>
      <a-empty v-if="!status?.methods?.length" description="尚無偵測結果，等待模擬資料…" />
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

.panel,
.control-panel {
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(11, 61, 46, 0.08);
  border-radius: 8px;
  padding: 16px;
}

.control-panel h3,
.panel h3 {
  margin: 0 0 12px;
  color: #0b3d2e;
}

.control-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.metrics {
  margin-top: 12px;
  display: grid;
  gap: 6px;
  font-size: 12px;
}

.metric-key {
  display: inline-block;
  min-width: 160px;
  color: #667;
  margin-right: 8px;
}
</style>
