export type SensorReading = {
  id: number
  ts: string
  pressure_in: number
  pressure_out: number
  flow_in: number
  flow_out: number
  temperature: number
}

export type MethodStatus = {
  method: string
  leak_suspected: boolean
  severity: string
  metrics: Record<string, number | string>
}

export type StatusResponse = {
  transport_status: string
  monitor_status: string
  content_type: string
  latest: SensorReading | null
  flow_change_rate: number | null
  pressure_change_rate: number | null
  methods: MethodStatus[]
  leak_injected: boolean
  transport_running: boolean
}

export type DetectionResult = {
  id: number
  ts: string
  method: string
  leak_suspected: boolean
  severity: string
  metrics: Record<string, number | string>
}

export type PipelineInfo = {
  id: number
  name: string
  length_m: number
  diameter_m: number
  content_type: string
}

export function useApi() {
  const config = useRuntimeConfig()
  const base = config.public.apiBase as string

  async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${base}${path}`, {
      headers: { 'Content-Type': 'application/json', ...(options?.headers || {}) },
      ...options,
    })
    if (!response.ok) {
      throw new Error(`API ${path} failed: ${response.status}`)
    }
    return (await response.json()) as T
  }

  return {
    getStatus: () => apiFetch<StatusResponse>('/api/status'),
    getLatestReadings: (limit = 60) =>
      apiFetch<SensorReading[]>(`/api/readings/latest?limit=${limit}`),
    getReadings: (from: string, to: string) =>
      apiFetch<SensorReading[]>(
        `/api/readings?from=${encodeURIComponent(from)}&to=${encodeURIComponent(to)}`,
      ),
    getDetections: (from: string, to: string) =>
      apiFetch<DetectionResult[]>(
        `/api/detections?from=${encodeURIComponent(from)}&to=${encodeURIComponent(to)}`,
      ),
    getPipeline: () => apiFetch<PipelineInfo>('/api/pipeline'),
    setLeak: (enabled: boolean) =>
      apiFetch<{ leak_injected: boolean; transport_running: boolean }>('/api/sim/leak', {
        method: 'POST',
        body: JSON.stringify({ enabled }),
      }),
    setTransport: (running: boolean) =>
      apiFetch<{ leak_injected: boolean; transport_running: boolean }>('/api/sim/transport', {
        method: 'POST',
        body: JSON.stringify({ running }),
      }),
  }
}
