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
    loading: true
  },
  actions: {
    loadData ({commit}) {
      axios.get(URL + 'start').then((response) => {
        // console.log(response.data, this)
        commit('updateRecords', response.data)
        commit('changeLoadingState', false)
      })
    }
  },
  mutations: {
    updateRecords (state, data) {
      state.objects = data.objects
      state.page = data._page
      state.next = data._next
    },
    changeLoadingState (state, loading) {
      state.loading = loading
    }
  }
})
