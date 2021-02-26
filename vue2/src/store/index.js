import Vue from 'vue'
import Vuex from 'vuex'
import createLogger from 'vuex/dist/logger'
import createPersistedState from 'vuex-persistedstate'
import app from './modules/app'
import auth from './modules/auth'

Vue.use(Vuex)

const debug = process.env.NODE_ENV !== 'production'
const persisted = createPersistedState({
  key: 'ands',
  paths: [
    'auth.user', 'auth.fcm_token', 'app.dark', 'app.find',
    'app.last', 'app.bucket', 'app.values', 'app.uploaded',
    'app.objects', 'app.pages', 'app.next'
  ]
})
const plugins = [persisted]
if (debug) {
  plugins.push(createLogger({}))
}

const store = new Vuex.Store({
  strict: debug,
  modules: {
    app,
    auth
  },
  plugins
})

export default store
