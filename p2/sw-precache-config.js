module.exports = {
    staticFileGlobs: [
        '/index.html',
        '/manifest.json',
        '/images/*'
    ],
    navigateFallback: '/index.html',
    runtimeCaching: [{
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
                maxAgeSeconds: 12* 60 * 60,
                name: 'data-cache'
            }
        }
    }]
};
