import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'
import VueAxios from 'vue-axios'

Vue.use(Vuex, VueAxios, axios)

const URL = '/api/'

export default new Vuex.Store({
  state: {
    objects: [],
    page: null,
    next: null,
    loading: false
  },
  actions: {
    resetData ({commit}) {
      commit('resetState')
    },
    loadData ({commit}, next) {
      commit('changeLoadingState', true)
      const params = (next && next === this.state.next) ? { _page: next } : {}
      axios.get(URL + 'start', {params: params}).then(response => {
        commit('updateRecords', response.data)
        commit('changeLoadingState', false)
      }).catch(e => {
        commit('changeLoadingState', false)
        console.log(e)
      })
    }
  },
  mutations: {
    resetState (state) {
      state.objects = []
      state.page = null
      state.next = null
      state.loading = false
    },
    updateRecords (state, data) {
      state.objects = state.objects.concat(data.objects)
      state.page = data._page
      state.next = data._next
    },
    changeLoadingState (state, loading) {
      state.loading = loading
    }
  }
})
