module.exports = {
    staticFileGlobs: [
        '/index.html',
        '/manifest.json',
        '/bower_components/webcomponentsjs/webcomponents-lite.min.js',
        '/images/*'
    ],
    navigateFallback: '/index.html',
    navigateFallbackWhitelist: [/^(?!.*\.html$).*/],
    runtimeCaching: [{
        urlPattern: /\/api\/.*/,
        handler: 'fastest',
        options: {
            cache: {
                maxEntries: 10,
                name: 'data-cache'
            }
        }
    }, {
        urlPattern: /^https:\/\/lh3\.googleusercontent\.com\/.*/,
        handler: 'cacheOnly',
        options: {
            cache: {
                maxEntries: 100,
                name: 'image-cache'
            }
        }
    }]
};
