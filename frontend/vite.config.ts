import fs from 'node:fs'
import path from 'node:path'
import { defineConfig, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'

function servePublicPrototypeIndex(): Plugin {
  const publicDir = path.resolve(__dirname, 'public')

  const resolvePublicIndex = (url?: string | null) => {
    if (!url) return null
    const pathname = url.split('?')[0].split('#')[0]
    if (!pathname.startsWith('/prototypes/') || !pathname.endsWith('/')) return null

    const relativePath = pathname.replace(/^\/+/, '')
    const filePath = path.join(publicDir, relativePath, 'index.html')
    if (!filePath.startsWith(publicDir) || !fs.existsSync(filePath)) return null

    return filePath
  }

  const middleware = (req: any, res: any, next: () => void) => {
    const filePath = resolvePublicIndex(req.url)
    if (!filePath) return next()

    res.statusCode = 200
    res.setHeader('Content-Type', 'text/html; charset=utf-8')
    res.end(fs.readFileSync(filePath, 'utf8'))
  }

  return {
    name: 'serve-public-prototype-index',
    configureServer(server) {
      server.middlewares.use(middleware)
    },
    configurePreviewServer(server) {
      server.middlewares.use(middleware)
    },
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), servePublicPrototypeIndex()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://localhost:8003',
        changeOrigin: true,
      },
    },
  },
})
