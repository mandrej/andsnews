module.exports = {
  pwa: {
    assetsVersion: process.env.VUE_APP_VERSION,
    workboxPluginMode: 'InjectManifest',
    workboxOptions: {
      swSrc: 'src/service-worker.js'
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
  assetsDir: 'static',
  productionSourceMap: false
}
