module.exports = {
  pwa: {
    assetsVersion: process.env.VUE_APP_VERSION,
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
        }
      ]
    },
    gcm_sender_id: '103953800507'
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
