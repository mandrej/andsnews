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
    paths: ['uploaded']
  })],
  state: {
    objects: [],
    current: null,
    page: null,
    next: null,
    loading: false,
    uploaded: []
  },
  // getters: {},
  actions: {
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
        .catch(e => {
          console.log(e)
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
          .catch(e => {
            console.log(e)
          })
      }
    },
    deleteRecord ({commit}, obj) {
      commit('updateCurrent', null)
      commit('changeRecords', obj)
      commit('changeUploaded', obj)

      HTTP.delete('delete/' + obj.safekey, {parms: {foo: 'bar'}})
        .then(response => {
          console.log(response.data)
        })
        .catch(e => {
          console.log(e)
        })
    },
    uploadList ({commit}, obj) {
      commit('updateUploaded', obj)
    },
    loadList ({commit}, next) {
      const params = (next) ? { _page: next } : {}
      commit('changeLoadingState', true)
      HTTP.get('start', {params: params}).then(response => {
        commit('updateRecords', response.data)
        commit('changeLoadingState', false)
      }).catch(e => {
        commit('changeLoadingState', false)
        console.log(e)
      })
    }
  },
  mutations: {
    updateCurrent (state, data) {
      state.current = data
    },
    updateRecords (state, data) {
      state.objects = state.objects.concat(data.objects)
      // const merged = state.objects.concat(data.objects)
      // state.objects = uniqBy(merged, p => p.safekey)
      state.page = data._page
      state.next = data._next
    },
    updateOneRecord (state, data) {
      const index = state.objects.findIndex(item => item.safekey === data.safekey)
      if (index !== -1) {
        state.objects[index] = data
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
