import fs from 'node:fs'
import path from 'node:path'
import { defineConfig, loadEnv, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'

function prototypeRoots(): string[] {
  const roots = [
    path.resolve(__dirname, 'public'),
    path.resolve(__dirname, 'dist'),
  ]
  const worktrees = process.env.CRYPTOFAROL_WORKTREES
    || '/srv/apps/dev/criptofarol/crypto-worktrees'
  if (!fs.existsSync(worktrees)) return roots
  for (const name of fs.readdirSync(worktrees)) {
    const publicDir = path.join(worktrees, name, 'frontend', 'public')
    if (fs.existsSync(publicDir)) roots.push(publicDir)
  }
  return roots
}

function servePublicPrototypeIndex(): Plugin {
  const resolvePrototypeFile = (url?: string | null) => {
    if (!url) return { kind: 'skip' as const }
    const pathname = url.split('?')[0].split('#')[0]
    if (pathname === '/prototypes' || pathname === '/prototypes/') {
      return { kind: 'skip' as const }
    }
    if (!pathname.startsWith('/prototypes/')) return { kind: 'skip' as const }

    const needsSlash = !pathname.endsWith('/') && !path.posix.extname(pathname)
    if (needsSlash) return { kind: 'redirect' as const, to: `${pathname}/` }

    let relativePath = pathname.replace(/^\/+/, '')
    if (relativePath.endsWith('/')) relativePath += 'index.html'
    if (relativePath.includes('..')) return { kind: 'missing' as const }

    for (const root of prototypeRoots()) {
      const filePath = path.resolve(root, relativePath)
      if (!filePath.startsWith(path.resolve(root) + path.sep) && filePath !== path.resolve(root)) {
        continue
      }
      if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
        return { kind: 'file' as const, filePath }
      }
    }
    return { kind: 'missing' as const }
  }

  const middleware = (req: any, res: any, next: () => void) => {
    const resolved = resolvePrototypeFile(req.url)
    if (resolved.kind === 'skip') return next()
    if (resolved.kind === 'redirect') {
      res.statusCode = 308
      res.setHeader('Location', resolved.to)
      res.end()
      return
    }
    if (resolved.kind === 'missing') {
      res.statusCode = 404
      res.setHeader('Content-Type', 'text/html; charset=utf-8')
      res.end(
        '<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8"><title>Protótipo não encontrado</title></head>'
        + '<body><p>Protótipo ausente. O fallback SPA foi bloqueado.</p></body></html>',
      )
      return
    }
    const ext = path.extname(resolved.filePath)
    const types: Record<string, string> = {
      '.html': 'text/html; charset=utf-8',
      '.css': 'text/css; charset=utf-8',
      '.js': 'text/javascript; charset=utf-8',
      '.svg': 'image/svg+xml',
      '.png': 'image/png',
      '.jpg': 'image/jpeg',
      '.jpeg': 'image/jpeg',
      '.woff2': 'font/woff2',
    }
    res.statusCode = 200
    res.setHeader('Content-Type', types[ext] || 'application/octet-stream')
    res.end(fs.readFileSync(resolved.filePath))
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
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, __dirname, '')
  const proxyTarget = env.VITE_DEV_PROXY_TARGET || 'http://localhost:8003'

  return {
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
          target: proxyTarget,
          changeOrigin: true,
        },
      },
    },
  }
})
