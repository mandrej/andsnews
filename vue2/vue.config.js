module.exports = {
  pwa: {
    name: 'Andрејевићи'
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