module.exports = {
  pwa: {
    name: 'Andрејевићи',
    themeColor: '#ffffff',
    msTileColor: '#ffffff',
    assetsVersion: '201811101357',
    workboxOptions: {
      runtimeCaching: [
        {
          urlPattern: /^https:\/\/fonts.(?:googleapis|gstatic).com\/(.*)/,
          handler: 'cacheFirst',
          options: {
            cacheName: 'google-fonts'
          }
        },
        {
          urlPattern: /api/,
          handler: 'staleWhileRevalidate',
          options: {
            cacheName: 'data-cache',
            expiration: {
              maxEntries: 100,
              maxAgeSeconds: 2 * 60 * 60
            },
            cacheableResponse: {
              statuses: [0, 200]
            }
          }
        }
      ]
    }
  },

  devServer: {
    proxy: {
      '/api': {
        target: process.env.VUE_APP_PROXY + 'api',
        changeOrigin: true,
        pathRewrite: {
          '^/api': ''
        }
      },
      '/_ah': {
        target: process.env.VUE_APP_PROXY + '_ah',
        changeOrigin: true,
        pathRewrite: {
          '^/_ah': ''
        }
      }
    }
  },

  baseUrl: undefined,
  outputDir: undefined,
  assetsDir: 'static',
  runtimeCompiler: undefined,
  productionSourceMap: undefined,
  parallel: undefined,
  css: undefined,
  lintOnSave: undefined
}
