import Vue from 'vue'
import Vuex from 'vuex'
import createPersistedState from 'vuex-persistedstate'
import { HTTP } from '../../helpers/http'
import { FB, MESSAGING } from '../../helpers/fire'

Vue.use(Vuex)

function pushMessage (token) {
  HTTP.post('message', {token: token})
    .then(response => {
      console.log(response.data)
    })
    .catch(() => console.log('push message failed'))
}

export default new Vuex.Store({
  plugins: [createPersistedState({
    key: 'vuex',
    paths: ['user', 'filter', 'find', 'uploaded', 'fcm_token']
  })],
  state: {
    user: {},
    find: {},
    filter: {},
    uploaded: [],
    fcm_token: null,

    objects: [],
    pages: [],
    page: null, // unused
    next: null,
    current: {},
    tags: [],
    models: [],
    info: {},
    busy: false,
    clear: false
  },
  actions: {
    saveUser: ({commit}, user) => {
      if (user && user.uid) {
        FB.database().ref('users').child(user.uid).set({
          email: user.email,
          date: (new Date()).toISOString()
        })
      }
      commit('SAVE_USER', user)
    },
    saveFindForm: ({commit}, payload) => commit('SAVE_FIND_FORM', payload),
    changeCurrent: ({commit}, payload) => commit('SET_CURRENT', payload),
    changeFilter: ({commit}, payload) => {
      commit('SET_CLEAR', true)
      commit('CHANGE_FILTER', payload)
    },
    addRecord: ({commit}, obj) => {
      commit('ADD_UPLOADED', obj)
      commit('ADD_RECORD', obj)
    },
    saveRecord: ({commit}, obj) => {
      HTTP.put('photo/edit/' + obj.safekey, obj)
        .then(response => {
          const obj = response.data.rec
          commit('UPDATE_RECORD', obj)
          commit('SET_CURRENT', obj)
          commit('DELETE_UPLOADED', obj)
        })
    },
    deleteRecord: ({commit}, obj) => {
      commit('DELETE_RECORD', obj)
      commit('DELETE_UPLOADED', obj)
      HTTP.delete('delete/' + obj.safekey, {parms: {foo: 'bar'}})
        .then(response => {
          console.log(response.data)
        })
    },
    fetchRecords: ({commit, state}, next) => {
      let url = 'start'
      const params = (next) ? { _page: next } : {}
      const filter = {...state.filter}

      if (filter && filter.field) {
        if (filter.field === 'search') {
          url = ['search', filter.value].join('/')
        } else {
          url = ['photo', filter.field, filter.value].join('/')
        }
      }

      commit('SET_BUSY', true)
      HTTP.get(url, {params: params})
        .then(response => {
          if (state.clear) {
            commit('RESET_RECORDS')
            commit('SET_CLEAR', false)
          }
          commit('SET_BUSY', false)
          commit('UPDATE_RECORDS', response.data)
        })
        .catch(err => {
          commit('SET_BUSY', false)
          console.log(err)
        })
    },
    fetchTags: ({commit}) => {
      HTTP.get('suggest/Photo_tags')
        .then(response => {
          commit('UPDATE_TAGS', response.data)
        })
    },
    fetchModels: ({commit}) => {
      HTTP.get('suggest/Photo_model')
        .then(response => {
          commit('UPDATE_MODELS', response.data)
        })
    },
    fetchInfo: ({commit}) => {
      HTTP.get('info')
        .then(response => {
          commit('SET_INFO', response.data)
        })
    },
    getToken: ({commit, dispatch}) => {
      if (process.env.NODE_ENV === 'development') return

      MESSAGING.requestPermission()
        .then(() => {
          console.log('permission success')
          return MESSAGING.getToken()
        })
        .then(token => {
          commit('SET_TOKEN', token)
          dispatch('subscribeToken')
        })
        .catch(() => console.log('permission failed'))
    },
    subscribeToken: ({commit, state}) => {
      const ref = FB.database().ref('registrations')
      ref.child(state.fcm_token).set({
        date: (new Date()).toISOString()
      })
    },
    sendNotifications: ({commit, state}) => {
      const ref = FB.database().ref('registrations')
      ref.once('value', (shot) => {
        shot.forEach(child => {
          if (child.key !== state.fcm_token) {
            pushMessage(child.key)
          }
        })
      })
    }
  },
  mutations: {
    SAVE_USER (state, payload) {
      state.user = Object.assign(state.user, payload)
    },
    SET_CURRENT (state, payload) {
      state.current = Object.assign({}, payload)
    },
    SAVE_FIND_FORM (state, payload) {
      state.find = Object.assign(state.find, payload)
    },
    CHANGE_FILTER (state, payload) {
      state.filter = Object.assign({}, payload)
    },
    ADD_RECORD (state, obj) {
      const dates = state.objects.map(item => item.date)
      const idx = dates.findIndex(date => date < obj.date)
      state.objects.splice(idx, 0, obj)
    },
    ADD_UPLOADED (state, data) {
      state.uploaded = [...state.uploaded, data]
    },
    UPDATE_RECORDS (state, data) {
      state.objects = [...state.objects, ...data.objects]
      state.pages = [...state.pages, data._page]
      state.page = data._page
      state.next = data._next
    },
    UPDATE_RECORD (state, obj) {
      const idx = state.objects.findIndex(item => item.safekey === obj.safekey)
      state.objects.splice(idx, 1, obj)
    },
    RESET_RECORDS (state) {
      state.objects.length = 0
      state.pages.length = 0
      state.page = null
      state.next = null
    },
    DELETE_RECORD (state, obj) {
      const idx = state.objects.findIndex(item => item.safekey === obj.safekey)
      state.objects.splice(idx, 1)
    },
    DELETE_UPLOADED (state, obj) {
      const idx = state.uploaded.findIndex(item => item.safekey === obj.safekey)
      if (idx > -1) state.uploaded.splice(idx, 1)
    },
    UPDATE_TAGS (state, data) {
      state.tags = data
    },
    UPDATE_MODELS (state, data) {
      state.models = data
    },
    SET_INFO (state, payload) {
      state.info = Object.assign({}, payload)
    },
    SET_CLEAR (state, clear) {
      state.clear = clear
    },
    SET_BUSY (state, busy) {
      state.busy = busy
    },
    SET_TOKEN (state, token) {
      state.fcm_token = token
    }
  }
})
