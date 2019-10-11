const VuetifyLoaderPlugin = require('vuetify-loader/lib/plugin')

module.exports = {
  configureWebpack: {
    plugins: [
      new VuetifyLoaderPlugin()
    ]
  },

  pwa: {
    name: 'Andрејевићи',
    themeColor: '#ffffff',
    msTileColor: '#ffffff',
    assetsVersion: '201910111230',
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
          handler: 'staleWhileRevalidate',
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

  publicPath: undefined,
  outputDir: undefined,
  assetsDir: 'static',
  runtimeCompiler: undefined,
  productionSourceMap: undefined,
  parallel: undefined,
  css: undefined
}
