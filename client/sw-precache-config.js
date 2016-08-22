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
        handler: 'networkFirst',
        options: {
            cache: {
                maxEntries: 50,
                maxAgeSeconds: 2 * 60,
                name: 'data-cache'
            }
        }
    }]
};
