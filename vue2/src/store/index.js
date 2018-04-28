import Vue from 'vue'
import Vuex from 'vuex'
import createPersistedState from 'vuex-persistedstate'
import VueAxios from 'vue-axios'
import { HTTP } from '../../helpers/http'
import { MESSAGING } from '../../helpers/fire'
// import { isEqual } from 'lodash' // uniqBy

Vue.use(Vuex, VueAxios)

export default new Vuex.Store({
  plugins: [createPersistedState({
    key: 'vuex',
    paths: ['user', 'objects', 'pages', 'filter', 'find', 'page', 'next', 'uploaded']
  })],
  state: {
    user: {},
    objects: [],
    pages: [],
    filter: {},
    find: {},
    page: null,
    next: null,
    uploaded: [],

    tags: [],
    models: [],
    info: {},
    busy: false,
    fcm_token: null
  },
  // getters: {},
  actions: {
    saveUser: ({commit}, user) => commit('SAVE_USER', user),
    addRecord: ({commit}, obj) => commit('ADD_RECORD', obj),
    saveRecord: ({commit}, obj) => {
      HTTP.put('photo/edit/' + obj.safekey, obj)
        .then(response => {
          const obj = response.data.rec
          commit('UPDATE_RECORD', obj)
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
    addUploaded: ({commit}, obj) => commit('ADD_UPLOADED', obj),
    saveFindForm: ({commit}, payload) => commit('SAVE_FIND_FORM', payload),
    changeFilter: ({commit}, payload) => {
      commit('CHANGE_FILTER', payload)
      commit('RESET_RECORDS')
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
          commit('ADD_PAGE', response.data._page)
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
          commit('UPDATE_INFO', response.data)
        })
    },
    getToken: ({commit}) => {
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
    SAVE_USER (state, user) {
      state.user = Object.assign({}, user)
    },
    SAVE_FIND_FORM (state, find) {
      state.find = Object.assign({}, find)
    },
    CHANGE_FILTER (state, filter) {
      state.filter = Object.assign({}, filter)
    },
    ADD_RECORD (state, obj) {
      state.objects.push(obj)
    },
    UPDATE_RECORDS (state, data) {
      state.objects = state.objects.concat(data.objects)
      // const merged = state.objects.concat(data.objects)
      // state.objects = uniqBy(merged, p => p.safekey)
      state.page = data._page
      state.next = data._next
    },
    RESET_RECORDS (state) {
      state.objects = []
      state.page = null
      state.next = null
      state.pages = []
    },
    ADD_PAGE (state, page) {
      state.pages.push(page)
    },
    UPDATE_TAGS (state, data) {
      state.tags = data
    },
    UPDATE_MODELS (state, data) {
      state.models = data
    },
    UPDATE_RECORD (state, data) {
      const index = state.objects.map(item => item.safekey).indexOf(data.safekey)
      if (index !== -1) {
        state.objects.splice(index, 1, data)
      } else {
        state.objects.push(data)
      }
    },
    DELETE_RECORD (state, data) {
      const index = state.objects.map(item => item.safekey).indexOf(data.safekey)
      if (index !== -1) {
        state.objects.splice(index, 1)
      }
    },
    ADD_UPLOADED (state, data) {
      state.uploaded.push(data)
    },
    DELETE_UPLOADED (state, data) {
      const index = state.uploaded.map(item => item.safekey).indexOf(data.safekey)
      if (index !== -1) {
        state.uploaded.splice(index, 1)
      }
    },
    SET_BUSY (state, busy) {
      state.busy = busy
    },
    UPDATE_INFO (state, payload) {
      state.info = Object.assign({}, payload)
    },
    SET_TOKEN (state, payload) {
      state.fcm_token = payload
    }
  }
})
