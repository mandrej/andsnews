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
      urlPattern: /\/api\/photo\/tags\/new/,
      handler: 'networkOnly'
    }, {
      urlPattern: /\/api\/.*/,
      handler: 'fastest',
      options: {
        cache: {
          maxEntries: 100,
          maxAgeSeconds: 12 * 3600,
          name: 'data-cache'
        }
      }
    }, {
      urlPattern: /^https:\/\/lh3.*/,
      handler: 'fastest',
      options: {
        cache: {
          maxEntries: 100,
          maxAgeSeconds: 7 * 24 * 3600,
          name: 'image-cache'
        }
      }
    }]
};
