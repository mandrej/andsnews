import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'
import VueAxios from 'vue-axios'
// import _union from 'lodash/union'
// import _ from 'lodash'

Vue.use(Vuex, VueAxios, axios)

const URL = '/api/'

export default new Vuex.Store({
  state: {
    objects: [],
    current: null,
    page: null,
    next: null,
    loading: false
  },
  actions: {
    // resetData ({commit}) {
    //   commit('resetState')
    // },
    getData ({commit}, id) {
      const obj = this.state.objects.filter(item => item.safekey === id)
      if (obj.length === 1) {
        console.log('found: ', obj[0])
        commit('updateCurrent', obj[0])
      } else {
        axios.get(URL + id)
          .then(response => {
            console.log('axios: ', response.data)
            commit('updateCurrent', response.data)
          })
          .catch(e => {
            console.log(e)
          })
      }
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
    // resetState (state) {
    //   state.objects = []
    //   state.page = null
    //   state.next = null
    //   state.loading = false
    // },
    updateCurrent (state, data) {
      state.current = data
    },
    updateRecords (state, data) {
      state.objects = state.objects.concat(data.objects)
      // const objects = _.union(state.objects, data.objects, (item) => {
      // })
      // state.objects = objects
      state.page = data._page
      state.next = data._next
    },
    changeLoadingState (state, loading) {
      state.loading = loading
    }
  }
})
