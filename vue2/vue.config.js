const path = require('path')
const VuetifyLoaderPlugin = require('vuetify-loader/lib/plugin')

module.exports = {
  chainWebpack: config => {
    const types = ['vue-modules', 'vue', 'normal-modules', 'normal']
    types.forEach(type => addStyleResource(config.module.rule('stylus').oneOf(type)))
  },

  configureWebpack: {
    plugins: [
      new VuetifyLoaderPlugin()
    ]
  },

  pwa: {
    name: 'Andрејевићи',
    themeColor: '#ffffff',
    msTileColor: '#ffffff',
    assetsVersion: '201904141833',
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

  baseUrl: undefined,
  outputDir: undefined,
  assetsDir: 'static',
  runtimeCompiler: undefined,
  productionSourceMap: undefined,
  parallel: undefined,
  css: undefined,
  lintOnSave: undefined
}

function addStyleResource (rule) {
  rule.use('style-resource')
    .loader('style-resources-loader')
    .options({
      patterns: [
        path.resolve(__dirname, './src/styles/imports.styl')
      ]
    })
}
