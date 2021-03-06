/* eslint-disable no-undef */
// define a prefix for your cache names. It is recommended to use your project name
workbox.core.setCacheNameDetails({ prefix: 'andsnews' })

// Start of Precaching##########################
// __precacheManifest is the list of resources you want to precache. This list will be generated and imported automatically by workbox during build time
self.__precacheManifest = [].concat(self.__precacheManifest || [])
workbox.precaching.precacheAndRoute(self.__precacheManifest, {})
// End of Precaching############################

// Start of CachFirst Strategy##################
// all the api request which matchs the following pattern will use CacheFirst strategy for caching
workbox.routing.registerRoute(
  /https:\/\/get\.geojs\.io\/v1\/ip\/country\.json/,
  new workbox.strategies.CacheFirst()
)

self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting()
  }
})
