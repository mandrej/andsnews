module.exports = {
  pwa: {
    name: 'Andрејевићи',
    themeColor: '#000000',
    msTileColor: '#ffffff',
    workboxPluginMode: 'GenerateSW',
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
        urlPattern: /^https:\/\/lh3\.googleusercontent\.com\/(.*)/,
          handler: 'cacheFirst',
          options: {
            cacheName: 'image-cache',
            expiration: {
              maxEntries: 100
            }
          }
        },
        {
        urlPattern: /api/,
          handler: 'networkFirst',
          options: {
            cacheName: 'data-cache',
            expiration: {
              maxEntries: 100
            }
          }
        }
      ]
    }
  },
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:6060/api',
        changeOrigin: true,
        pathRewrite: {
          '^/api': ''
        }
      },
      '/_ah': {
        target: 'http://localhost:6060/_ah',
        changeOrigin: true,
        pathRewrite: {
          '^/_ah': ''
        }
      }
    }
  }
}
