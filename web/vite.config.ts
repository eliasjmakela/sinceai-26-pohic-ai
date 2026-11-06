import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// Static build only: the demo runs offline from `npm run preview` (PRODUCT.md §8).
export default defineConfig({
  plugins: [react(), tailwindcss()],
})
