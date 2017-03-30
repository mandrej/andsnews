module.exports = {
    staticFileGlobs: [
        '/index.html',
        '/manifest.json',
        '/bower_components/webcomponentsjs/webcomponents-lite.min.js',
        '/node_modules/redux/dist/redux.min.js',
        '/images/*'
    ],
    navigateFallback: '/index.html',
    runtimeCaching: [{
        urlPattern: /\/api\/photo\/tags\/new/,
        handler: 'networkFirst'
    }, {
        urlPattern: /\/api\/.*/,
        handler: 'fastest',
        options: {
            cache: {
                maxEntries: 100,
                maxAgeSeconds: 12* 60 * 60,
                name: 'data-cache'
            }
        }
    }]
};
