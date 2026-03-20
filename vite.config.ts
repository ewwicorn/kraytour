import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
    },
  },
  css: {
    devSourcemap: true,
    modules: {
      // Поведение CSS-модулей
      scopeBehaviour: 'local',
      globalModulePaths: [],
      generateScopedName: undefined,
      hashPrefix: '',
      localsConvention: 'camelCaseOnly',
    },
    preprocessorOptions: {
      scss: {
        // Автоматически подключаем helpers во все SCSS-файлы
        additionalData: `
          @use '@/app/styles/helpers' as *;
        `,
      },
      less: {},
      stylus: {},
    },
  },
})