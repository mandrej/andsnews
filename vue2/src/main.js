import 'core-js/stable'
import 'regenerator-runtime/runtime'
import Vue from 'vue'
import vuetify from './plugins/vuetify'
import './plugins/axios'
import App from './App.vue'
import router from './router'
import './registerServiceWorker'
import configureStore from './store'

Vue.config.productionTip = false
Vue.config.performance = process.env.NODE_ENV !== 'production'

new Vue({
  vuetify,
  router,
  store: configureStore(),
  render: h => h(App)
}).$mount('#app')
