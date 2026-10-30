import type { SensorReading } from './useApi'

export function buildFlowTraces(readings: SensorReading[]) {
  const x = readings.map((r) => r.ts)
  return [
    {
      x,
      y: readings.map((r) => r.flow_in),
      type: 'scatter',
      mode: 'lines',
      name: '入口流量',
      line: { color: '#1677ff' },
    },
    {
      x,
      y: readings.map((r) => r.flow_out),
      type: 'scatter',
      mode: 'lines',
      name: '出口流量',
      line: { color: '#52c41a' },
    },
  ]
}

export function buildPressureTraces(readings: SensorReading[]) {
  const x = readings.map((r) => r.ts)
  return [
    {
      x,
      y: readings.map((r) => r.pressure_in),
      type: 'scatter',
      mode: 'lines',
      name: '入口壓力',
      line: { color: '#fa8c16' },
    },
    {
      x,
      y: readings.map((r) => r.pressure_out),
      type: 'scatter',
      mode: 'lines',
      name: '出口壓力',
      line: { color: '#eb2f96' },
    },
  ]
}

export const plotLayoutBase = {
  margin: { t: 32, r: 24, b: 48, l: 56 },
  paper_bgcolor: 'transparent',
  plot_bgcolor: 'transparent',
  legend: { orientation: 'h' as const },
  xaxis: { title: '時間' },
  autosize: true,
}
