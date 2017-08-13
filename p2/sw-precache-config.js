module.exports = {
  staticFileGlobs: [
    '/index.html',
    '/manifest.json',
    '/bower_components/webcomponentsjs/webcomponents-lite.js',
    '/images/*'
  ],
  navigateFallback: '/index.html',
  navigateFallbackWhitelist: [/^(?!.*\.html$|\/data\/).*/],
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
      urlPattern: /\/api\/photo\/tags\/new/,
      handler: 'networkFirst'
    }, {
      urlPattern: /\/api\/.*/,
      handler: 'fastest',
      options: {
        cache: {
          maxEntries: 100,
          maxAgeSeconds: 24 * 60 * 60,
          name: 'data-cache'
        }
      }
    }, {
      urlPattern: /^https:\/\/lh3.*/,
      handler: 'fastest',
      options: {
        cache: {
          maxEntries: 500,
          maxAgeSeconds: 24 * 60 * 60,
          name: 'image-cache'
        }
      }
    }]
};
