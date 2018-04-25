import Vue from 'vue'
import Vuex from 'vuex'
import createPersistedState from 'vuex-persistedstate'
import VueAxios from 'vue-axios'
import { HTTP } from '../../helpers/http'
import { MESSAGING } from '../../helpers/fire'
import { isEqual } from 'lodash' // uniqBy

Vue.use(Vuex, VueAxios)

export default new Vuex.Store({
  plugins: [createPersistedState({
    key: 'vuex',
    paths: ['user', 'find', 'uploaded']
  })],
  state: {
    user: {},
    objects: [],
    pages: [],
    filter: {},
    find: {},
    page: null,
    next: null,
    busy: false,
    uploaded: [],
    tags: [],
    models: [],
    info: {},
    fcm_token: null
  },
  // getters: {},
  actions: {
    signIn ({commit}, user) {
      commit('updateUser', user)
    },
    changeUploaded ({commit}, obj) {
      commit('removeFromUploaded', obj)
    },
    saveRecord ({commit}, obj) {
      HTTP.put('photo/edit/' + obj.safekey, obj)
        .then(response => {
          const obj = response.data.rec
          commit('updateOneRecord', obj)
          commit('removeFromUploaded', obj)
        })
    },
    deleteRecord ({commit}, obj) {
      commit('removeFromRecords', obj)
      commit('removeFromUploaded', obj)

      HTTP.delete('delete/' + obj.safekey, {parms: {foo: 'bar'}})
        .then(response => {
          console.log(response.data)
        })
    },
    uploadList ({commit}, obj) {
      commit('updateUploaded', obj)
    },
    changeFind ({commit}, payload) {
      commit('updateFind', payload)
    },
    changeFilter ({state, commit, dispatch}, payload) {
      if (!isEqual(state.filter, payload)) {
        commit('updateFilter', payload)
        commit('resetRecords')
        commit('resetPages')
        // if (!isEmpty(payload)) dispatch('loadList')
      }
    },
    loadList ({commit, state}, next) {
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

      commit('changeLoadingState', true)
      HTTP.get(url, {params: params})
        .then(response => {
          commit('changeLoadingState', false)
          commit('updatePages', response.data._page)
          commit('updateRecords', response.data)
        })
        .catch(err => {
          commit('changeLoadingState', false)
          console.log(err)
        })
    },
    getTags ({commit}) {
      HTTP.get('suggest/Photo_tags')
        .then(response => {
          commit('updateTags', response.data)
        })
    },
    getModels ({commit}) {
      HTTP.get('suggest/Photo_model')
        .then(response => {
          commit('updateModels', response.data)
        })
    },
    getInfo ({commit}) {
      HTTP.get('info')
        .then(response => {
          commit('updateInfo', response.data)
        })
    },
    getToken ({commit}) {
      MESSAGING.requestPermission()
        .then(() => {
          console.log('permission success')
          return MESSAGING.getToken()
        })
        .then(token => {
          commit('setToken', token)
        })
        .catch(() => console.log('permission failed'))
    }
  },
  mutations: {
    updateUser (state, user) {
      state.user = Object.assign({}, user)
    },
    updateFind (state, find) {
      state.find = Object.assign({}, find)
    },
    updateFilter (state, filter) {
      state.filter = Object.assign({}, filter)
    },
    updateRecords (state, data) {
      state.objects = state.objects.concat(data.objects)
      // const merged = state.objects.concat(data.objects)
      // state.objects = uniqBy(merged, p => p.safekey)
      state.page = data._page
      state.next = data._next
    },
    resetRecords (state) {
      state.objects = []
      state.page = null
      state.next = null
    },
    updatePages (state, page) {
      state.pages.push(page)
    },
    resetPages (state) {
      state.pages = []
    },
    updateTags (state, data) {
      state.tags = data
    },
    updateModels (state, data) {
      state.models = data
    },
    updateOneRecord (state, data) {
      const index = state.objects.findIndex(item => item.safekey === data.safekey)
      if (index !== -1) {
        state.objects.splice(index, 1, data)
      } else {
        state.objects.push(data)
      }
    },
    removeFromRecords (state, data) {
      const index = state.objects.findIndex(item => item.safekey === data.safekey)
      if (index !== -1) {
        state.objects.splice(index, 1)
      }
    },
    updateUploaded (state, data) {
      state.uploaded.push(data)
    },
    removeFromUploaded (state, data) {
      const index = state.uploaded.findIndex(item => item.safekey === data.safekey)
      if (index !== -1) {
        state.uploaded.splice(index, 1)
      }
    },
    changeLoadingState (state, busy) {
      state.busy = busy
    },
    updateInfo (state, payload) {
      state.info = Object.assign({}, payload)
    },
    setToken (state, payload) {
      state.fcm_token = payload
    }
  }
})
