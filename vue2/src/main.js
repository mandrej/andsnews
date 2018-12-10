import '@babel/polyfill'
import Vue from 'vue'
import './plugins/vuetify'
import './plugins/axios'
import App from './App.vue'
import router from './router'
import './registerServiceWorker'
import configureStore from './store'

// Instance Properties
Vue.prototype.$authors = [
  'milan.andrejevic@gmail.com',
  'mihailo.genije@gmail.com',
  'svetlana.andrejevic@gmail.com',
  'ana.devic@gmail.com',
  'dannytaboo@gmail.com',
  'zile.zikson@gmail.com'
]
// user.uid for           milan.andrejevic@gmail.com      mihailo.genije@gmail.com
Vue.prototype.$admins = ['j8ezW5PBwMMnzrUvDA9ucYOOmrD3', 'vlRwHqVZNfOpr3FRqQZGqT2M2HA2']

Vue.config.productionTip = false

new Vue({
  router,
  store: configureStore(),
  render: h => h(App)
}).$mount('#app')
