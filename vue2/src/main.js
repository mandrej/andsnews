// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
import store from './store'
import firebase from 'firebase'

import Vuetify from 'vuetify'
import 'vuetify/dist/vuetify.min.css'

Vue.config.productionTip = false

const config = {
  apiKey: 'AIzaSyBj5uKo0P_mir_ChQ_syx_kUQ_g7nkNy6M',
  authDomain: 'andsnews.firebaseapp.com',
  databaseURL: 'https://andsnews.firebaseio.com',
  projectId: 'andsnews',
  storageBucket: 'andsnews.appspot.com',
  messagingSenderId: '719127177629'
}
const FB = firebase.initializeApp(config)
Vue.prototype.$FireAuth = FB.auth()
Vue.prototype.$Google = new firebase.auth.GoogleAuthProvider().addScope('email')
Vue.prototype.$FireBase = FB.database().ref()
Vue.prototype.$FireMessaging = FB.messaging().usePublicVapidKey('BEMvPS8oRWveXcM6M_uBdQvDFZqvYKUOnUa22hVvMMlSMFr_04rI3G3BjJWW7EZKSqkM2mchPP3tReV4LY0Y45o')

Vue.use(Vuetify, {
  theme: {
    primary: '#1976D2',
    secondary: '#424242',
    accent: '#82B1FF',
    error: '#FF5252',
    info: '#2196F3',
    success: '#4CAF50',
    warning: '#FFC107'
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
