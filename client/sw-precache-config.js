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
        handler: 'networkFirst',
        options: {
            cache: {
                maxEntries: 20,
                name: 'data-cache'
            }
        }
    }]
};
