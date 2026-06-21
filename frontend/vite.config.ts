import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

function normalizeProxyTarget(raw: string): string {
  return raw.replace(/^http:\/\/localhost/i, 'http://127.0.0.1')
}

const DEFAULT_SHOPS_PROXY_TARGET = 'http://127.0.0.1:8000'
const DEFAULT_LOGIN_PROXY_TARGET = 'http://127.0.0.1:8001'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const shopsOrigin = env.VITE_SHOPS_ORIGIN ?? ''
  const loginOrigin = env.VITE_LOGIN_ORIGIN ?? ''
  const useShopsProxy = shopsOrigin.startsWith('/')
  const useLoginProxy = loginOrigin.startsWith('/')
  const shopsProxyTarget = normalizeProxyTarget(
    env.VITE_SHOPS_PROXY_TARGET || DEFAULT_SHOPS_PROXY_TARGET,
  )
  const loginProxyTarget = normalizeProxyTarget(
    env.VITE_LOGIN_PROXY_TARGET || DEFAULT_LOGIN_PROXY_TARGET,
  )

  const proxy: Record<string, object> = {}
  if (useShopsProxy) {
    proxy['/api/shops'] = {
      target: shopsProxyTarget,
      changeOrigin: true,
      rewrite: (path: string) => path.replace(/^\/api\/shops/, ''),
      timeout: 120_000,
      proxyTimeout: 120_000,
    }
  }
  if (useLoginProxy) {
    proxy['/api/auth'] = {
      target: loginProxyTarget,
      changeOrigin: true,
      rewrite: (path: string) => path.replace(/^\/api\/auth/, ''),
    }
  }

  return {
    plugins: [vue()],
    server: {
      host: '127.0.0.1',
      port: 5173,
      strictPort: false,
      proxy: Object.keys(proxy).length > 0 ? proxy : undefined,
    },
  }
})
