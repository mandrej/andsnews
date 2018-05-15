// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
import store from './store'

import Vuetify from 'vuetify'
import 'vuetify/dist/vuetify.min.css'

Vue.config.productionTip = false

if (
  process.env.NODE_ENV === 'production' &&
  (location.protocol === 'https:' || location.host.match(/(localhost|127.0.0.1)/)) &&
  navigator.serviceWorker
) {
  navigator.serviceWorker.register('/service-worker.js')
}

Vue.use(Vuetify, {
  theme: {
    primary: '#3F51B5',
    secondary: '#536DFE',
    accent: '#FFC107',
    error: '#f44336',
    warning: '#ffeb3b',
    info: '#2196f3',
    success: '#4caf50'
  }
})

/* eslint-disable no-new */
new Vue({
  el: '#app',
  store,
  router,
  components: { App },
  template: '<App/>'
})
