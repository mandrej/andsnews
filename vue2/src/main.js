import Vue from 'vue'
import vuetify from '@/plugins/vuetify'
import '@/plugins/axios'
import '@/plugins/dayjs'
import App from './App.vue'
import router from './router'
import './registerServiceWorker'
import store from './store'
import mitt from 'mitt'

Vue.config.productionTip = false
Vue.config.performance = process.env.NODE_ENV !== 'production'
Vue.prototype.$eventBus = mitt()

new Vue({
  vuetify,
  router,
  store,
  render: h => h(App)
}).$mount('#app')
