module.exports = {
  pwa: {
    name: 'Andрејевићи',
    themeColor: '#ffffff',
    msTileColor: '#ffffff',
    assetsVersion: process.env.VUE_APP_VERSION,
    iconPaths: {
      favicon32: 'static/img/icons/favicon-32x32.png',
      favicon16: 'static/img/icons/favicon-16x16.png',
      appleTouchIcon: 'static/img/icons/apple-touch-icon-152x152.png',
      // maskIcon: 'static/img/icons/safari-pinned-tab.svg',
      msTileImage: 'static/img/icons/msapplication-icon-144x144.png'
    },
    workboxOptions: {
      runtimeCaching: [
        {
          urlPattern: /^https:\/\/fonts.(?:googleapis|gstatic).com\/(.*)/,
          handler: 'StaleWhileRevalidate',
          options: {
            cacheName: 'google'
          }
        },
        {
          urlPattern: /^https:\/\/lh3.googleusercontent.com\/(.*)/,
          handler: 'StaleWhileRevalidate',
          options: {
            cacheName: 'google'
          }
        },
        {
          urlPattern: /api/,
          handler: 'StaleWhileRevalidate',
          options: {
            cacheName: 'data-cache',
            expiration: {
              maxEntries: 100,
              maxAgeSeconds: 3600
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
      }
    }
  },

  transpileDependencies: ['vuetify'],
  assetsDir: 'static'
}
