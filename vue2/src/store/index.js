import Vue from 'vue'
import Vuex from 'vuex'
import createPersistedState from 'vuex-persistedstate'
import createLogger from 'vuex/dist/logger'
import modules from './modules'

Vue.use(Vuex)

const APP_KEY = 'ands'

const isNotProd = process.env.NODE_ENV !== 'production'
const isNotTest = process.env.NODE_ENV !== 'test'

const createStore = () => {
  const store = new Vuex.Store({
    modules,
    strict: isNotProd,
    plugins: []
      .concat(
        isNotTest
          ? [createPersistedState({ key: APP_KEY })]
          : ['user', 'fcm_token', 'find', 'last', 'dark', 'uploaded']
      )
      .concat(isNotProd ? [createLogger()] : [])
  })
  if (module.hot) {
    // accept actions and mutations as hot modules
    module.hot.accept(['./modules'], () => {
      // require the updated modules
      // have to add .default here due to babel 6 module output
      import('./modules').then(newModules => {
        // swap in the new actions and mutations
        store.hotUpdate({
          modules: newModules.default
        })
      })
    })
  }
  return store
}

export default createStore
