import Vue from 'vue'
import Vuex from 'vuex'
import createPersistedState from 'vuex-persistedstate'
import VueAxios from 'vue-axios'
import { HTTP } from '../../helpers/http'
import { MESSAGING } from '../../helpers/fire'

Vue.use(Vuex, VueAxios)

export default new Vuex.Store({
  plugins: [createPersistedState({
    key: 'vuex',
    paths: ['user', 'filter', 'find', 'uploaded', 'objects', 'pages', 'page', 'next']
  })],
  state: {
    user: {},
    filter: {},
    find: {},
    uploaded: [],
    objects: [],
    pages: [],
    page: null, // unused
    next: null,

    current: {},
    tags: [],
    models: [],
    info: {},
    busy: false,
    fcm_token: null
  },
  actions: {
    saveUser: ({commit}, user) => commit('SAVE_USER', user),
    saveFindForm: ({commit}, payload) => commit('SAVE_FIND_FORM', payload),
    changeCurrent: ({commit}, payload) => commit('SET_CURRENT', payload),
    changeFilter: ({commit}, payload) => {
      commit('RESET_RECORDS')
      commit('CHANGE_FILTER', payload)
    },
    addRecord: ({commit}, obj) => commit('ADD_RECORD', obj),
    addUploaded: ({commit}, obj) => commit('ADD_UPLOADED', obj),
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
    fetchObject: ({commit}, id) => {
      commit('SET_BUSY', true)
      HTTP.get(id)
        .then(response => {
          commit('SET_BUSY', false)
          commit('SET_CURRENT', response.data)
          console.log(response.data)
        })
    },
    fetchRecords: ({commit, state}, next) => {
      let url = 'start'
      const params = (next) ? { _page: next } : {}
      const saved = {...state.filter}

      if (saved && saved.field) {
        if (saved.field === 'search') {
          url = ['search', saved.value].join('/')
        } else {
          url = ['photo', saved.field, saved.value].join('/')
        }
      }

      commit('SET_BUSY', true)
      HTTP.get(url, {params: params})
        .then(response => {
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
    getToken: ({commit}) => {
      if (process.env.NODE_ENV === 'development') return

      MESSAGING.requestPermission()
        .then(() => {
          console.log('permission success')
          return MESSAGING.getToken()
        })
        .then(token => {
          commit('SET_TOKEN', token)
        })
        .catch(() => console.log('permission failed'))
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
    SET_BUSY (state, busy) {
      state.busy = busy
    },
    SET_TOKEN (state, token) {
      state.fcm_token = token
    }
  }
})
