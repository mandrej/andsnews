import Vue from 'vue'
import Vuex from 'vuex'
import VueAxios from 'vue-axios'
import { HTTP } from '../../config/http'
// import uniqBy from 'lodash/uniqBy'

Vue.use(Vuex, VueAxios)

export default new Vuex.Store({
  state: {
    objects: [],
    current: null,
    page: null,
    next: null,
    loading: false,
    uploaded: []
  },
  // getters: {
  //   record: state => state.current
  // },
  actions: {
    // resetData ({commit}) {
    //   commit('resetState')
    // },
    saveRecord ({commit}, id) {
      HTTP.put('photo/edit/' + id, this.state.current)
        .then(response => {
          commit('changeCurrent', response.data.rec)
        })
        .catch(e => {
          console.log(e)
        })
    },
    getRecord ({commit}, id) {
      const obj = this.state.objects.filter(item => item.safekey === id)
      if (obj.length === 1) {
        commit('changeCurrent', obj[0])
      } else {
        HTTP.get(id)
          .then(response => {
            commit('changeCurrent', response.data)
          })
          .catch(e => {
            console.log(e)
          })
      }
    },
    uploadList ({commit}, list) {
      const $list = list
      const upload = item => {
        HTTP.post('photo/add', item)
          .then(response => {
            commit('updateUploaded', response.data)
          })
          .catch(e => {
            console.log(e)
          })
      }
      for (let i = 0; i < $list.length; i++) {
        upload($list[i])
      }
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
    // resetState (state) {
    //   state.objects = []
    //   state.page = null
    //   state.next = null
    //   state.loading = false
    // },
    changeCurrent (state, data) {
      state.current = data
    },
    updateRecords (state, data) {
      state.objects = state.objects.concat(data.objects)
      // const merged = state.objects.concat(data.objects)
      // state.objects = uniqBy(merged, p => p.safekey)
      state.page = data._page
      state.next = data._next
    },
    changeLoadingState (state, loading) {
      state.loading = loading
    },
    updateUploaded (state, data) {
      state.uploaded.push(data)
    }
  }
})
