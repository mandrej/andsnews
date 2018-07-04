import '@babel/polyfill'
import Vue from 'vue'
import './plugins/vuetify'
import './plugins/axios'
import App from './App.vue'
import router from './router'
import './registerServiceWorker'
import configureStore from './store';

Vue.config.productionTip = false

new Vue({
  router,
  store: configureStore(),
  render: h => h(App)
}).$mount('#app')
