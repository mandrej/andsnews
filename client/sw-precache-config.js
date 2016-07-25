module.exports = {
    staticFileGlobs: [
        '/index.html',
        '/manifest.json',
        '/bower_components/webcomponentsjs/webcomponents-lite.min.js',
        '/images/*'
    ],
    navigateFallback: '/index.html',
    runtimeCaching: [{
        urlPattern: /\/api\/.*/,
        handler: 'fastest',
        options: {
            cache: {
                maxEntries: 20,
                name: 'data-cache'
            }
        }
    }]
};
