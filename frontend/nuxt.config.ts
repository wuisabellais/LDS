import { fileURLToPath } from 'node:url'

const dayjsEsm = fileURLToPath(new URL('./node_modules/dayjs/esm/index.js', import.meta.url))
const dayjsPlugin = fileURLToPath(new URL('./node_modules/dayjs/esm/plugin', import.meta.url))

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  ssr: false,
  css: ['ant-design-vue/dist/reset.css'],
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://127.0.0.1:8000',
    },
  },
  build: {
    transpile: ['ant-design-vue'],
  },
  vite: {
    resolve: {
      alias: [
        { find: /^dayjs$/, replacement: dayjsEsm },
        { find: /^dayjs\/plugin\/(.+)$/, replacement: `${dayjsPlugin}/$1` },
      ],
    },
    optimizeDeps: {
      include: ['ant-design-vue', 'plotly.js-dist-min', 'dayjs'],
    },
  },
})
