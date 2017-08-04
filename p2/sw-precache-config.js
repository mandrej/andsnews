module.exports = {
  staticFileGlobs: [
    '/index.html',
    '/manifest.json',
    '/bower_components/webcomponentsjs/webcomponents-loader.js',
    '/images/*'
  ],
  runtimeCaching: [
    {
      urlPattern: /\/bower_components\/webcomponentsjs\/.*.js/,
      handler: 'fastest',
      options: {
        cache: {
          name: 'webcomponentsjs-polyfills-cache'
        }
      }
    }, {
      urlPattern: /\/_ah\/.*/,
      handler: 'networkFirst'
    }, {
      urlPattern: /\/api\/photo\/tags\/new/,
      handler: 'networkFirst'
    }, {
      urlPattern: /\/api\/.*/,
      handler: 'fastest',
      options: {
        cache: {
          maxEntries: 100,
          maxAgeSeconds: 12 * 60 * 60,
          name: 'data-cache'
        }
      }
    }]
};