import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// The app is only ever reached in production through the landing site's
// /app rewrite (quanta-landing → /app/* → this deployment), so its asset
// URLs need the /app/ prefix baked in at build time. Local dev keeps
// serving from root for convenience.
// https://vite.dev/config/
export default defineConfig(({ command }) => ({
  plugins: [react()],
  base: command === 'build' ? '/app/' : '/',
}))
