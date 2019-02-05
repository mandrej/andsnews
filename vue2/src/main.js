import '@babel/polyfill'
import Vue from 'vue'
import './plugins/vuetify'
import './plugins/axios'
import App from './App.vue'
import router from './router'
import './registerServiceWorker'
import configureStore from './store'

// Instance Properties
// user.uid for           milan.andrejevic@gmail.com      mihailo.genije@gmail.com
Vue.prototype.$admins = ['j8ezW5PBwMMnzrUvDA9ucYOOmrD3', 'vlRwHqVZNfOpr3FRqQZGqT2M2HA2']

Vue.config.productionTip = false
Vue.config.performance = process.env.NODE_ENV !== 'production'

new Vue({
  router,
  store: configureStore(),
  render: h => h(App)
}).$mount('#app')
