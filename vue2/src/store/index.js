import Vue from 'vue'
import Vuex from 'vuex'
import createPersistedState from 'vuex-persistedstate'
import VueAxios from 'vue-axios'
import { HTTP } from '../../config/http'
// import uniqBy from 'lodash/uniqBy'

Vue.use(Vuex, VueAxios)

export default new Vuex.Store({
  plugins: [createPersistedState({
    key: 'vuex',
    paths: ['user', 'find', 'uploaded']
  })],
  state: {
    user: {
      name: '',
      email: '',
      uid: null,
      isAuthorized: false,
      isAdmin: false
    },
    objects: [],
    filter: {},
    find: {
      tags: [],
      text: '',
      year: '',
      month: '',
      model: '',
      author: '',
      color: ''
    },
    current: null,
    page: null,
    next: null,
    loading: false,
    uploaded: [],
    tags: [],
    models: []
  },
  // getters: {},
  actions: {
    signIn ({commit}, user) {
      commit('updateUser', user)
    },
    changeCurrent ({commit}, obj) {
      commit('updateCurrent', obj)
    },
    changeRecords ({commit}, obj) {
      commit('removeFromRecords', obj)
    },
    changeUploaded ({commit}, obj) {
      commit('removeFromUploaded', obj)
    },
    saveRecord ({commit}, id) {
      HTTP.put('photo/edit/' + id, this.state.current)
        .then(response => {
          const obj = response.data.rec
          commit('updateCurrent', obj)
          commit('updateOneRecord', obj)
          commit('removeFromUploaded', obj)
        })
        .catch(err => {
          console.log(err)
        })
    },
    getRecord ({commit}, id) {
      const obj = this.state.objects.filter(item => item.safekey === id)
      if (obj.length === 1) {
        commit('updateCurrent', obj[0])
      } else {
        HTTP.get(id)
          .then(response => {
            commit('updateCurrent', response.data)
          })
          .catch(err => {
            console.log(err)
          })
      }
    },
    deleteRecord ({commit}, obj) {
      commit('updateCurrent', null)
      commit('removeFromRecords', obj)
      commit('removeFromUploaded', obj)

      HTTP.delete('delete/' + obj.safekey, {parms: {foo: 'bar'}})
        .then(response => {
          console.log(response.data)
        })
        .catch(err => {
          console.log(err)
        })
    },
    uploadList ({commit}, obj) {
      commit('updateUploaded', obj)
    },
    changeFind ({commit}, payload) {
      commit('updateFind', payload)
    },
    changeFilter ({commit}, payload) {
      commit('updateFilter', payload)
      commit('resetRecords')
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
      console.log(url, params)

      commit('changeLoadingState', true)
      HTTP.get(url, {params: params})
        .then(response => {
          commit('changeLoadingState', false)
          commit('updateRecords', response.data)
        })
        .catch(err => {
          commit('changeLoadingState', false)
          console.log(err)
        })
    },
    clearList ({commit}) {
      commit('resetRecords')
    },
    getTags ({commit}) {
      HTTP.get('suggest/Photo_tags')
        .then(response => {
          commit('updateTags', response.data)
        })
        .catch(err => {
          console.log(err)
        })
    },
    getModels ({commit}) {
      HTTP.get('suggest/Photo_model')
        .then(response => {
          commit('updateModels', response.data)
        })
        .catch(err => {
          console.log(err)
        })
    }
  },
  mutations: {
    updateUser (state, user) {
      state.user = Object.assign({}, user)
    },
    updateCurrent (state, data) {
      state.current = data
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
    changeLoadingState (state, loading) {
      state.loading = loading
    }
  }
})
