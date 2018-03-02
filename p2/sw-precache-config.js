module.exports = {
  staticFileGlobs: [
    '/index.html',
    '/manifest.json',
    '/bower_components/webcomponentsjs/webcomponents-loader.js',
    '/src/*',
    '/images/*'
  ],
  navigateFallback: '/index.html',
  navigateFallbackWhitelist: [],
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
      urlPattern: /\/service-worker\.js/,
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
          name: 'data-cache',
          maxAgeSeconds: 60 * 60
        }
      }
    }, {
      urlPattern: /^https:\/\/lh3.*/,
      handler: 'fastest',
      options: {
        cache: {
          maxEntries: 300,
          name: 'image-cache'
        }
      }
    }]
};
