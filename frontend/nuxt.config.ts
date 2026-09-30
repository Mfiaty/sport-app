// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },

  modules: ['@vite-pwa/nuxt'],

  app: {
    head: {
      title: 'Mon app foot',
      htmlAttrs: { lang: 'fr' },
      meta: [
        { name: 'description', content: 'Apprends à comprendre le football, pas à pas.' },
        { name: 'theme-color', content: '#16a34a' },
      ],
    },
  },

  pwa: {
    registerType: 'autoUpdate',
    manifest: {
      name: 'Mon app foot',
      short_name: 'Foot',
      description: 'Apprends à comprendre le football, pas à pas.',
      lang: 'fr',
      theme_color: '#16a34a',
      background_color: '#ffffff',
      display: 'standalone',
      icons: [
        { src: '/icons/icon-192.png', sizes: '192x192', type: 'image/png' },
        { src: '/icons/icon-512.png', sizes: '512x512', type: 'image/png' },
      ],
    },
    workbox: {
      navigateFallback: '/',
    },
    devOptions: {
      enabled: true,
      type: 'module',
    },
  },
})