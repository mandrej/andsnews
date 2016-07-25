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
                maxEntries: 20,
                name: 'data-cache'
            }
        }
    }, {
        urlPattern: /^https:\/\/lh3\.googleusercontent\.com\/.*/,
        handler: 'fastest',
        options: {
            cache: {
                maxEntries: 200,
                name: 'image-cache'
            }
        }
    }]
};
