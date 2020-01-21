/* eslint no-console: ["error", { allow: ["warn", "error"] }] */
// export const RESET = 'RESET';
import Vue from 'vue'
import { EventBus } from '@/helpers/event-bus'
import debounce from 'lodash/debounce'
import querystring from 'querystring'

const axios = Vue.axios
const LIMIT = 24

const initialState = {
  find: {},
  uploaded: [],

  last: {},
  total: 0,
  values: {},

  objects: [],
  count: 0,
  pages: [],
  next: null,
  error: '',

  busy: false,
  clear: false
}

const actions = {
  // reset: ({ commit }) => commit(RESET),
  saveFindForm: ({ commit }, payload) => commit('SAVE_FIND_FORM', payload),
  changeFilter: ({ commit, dispatch }, payload) => {
    if (payload.reset) {
      commit('SET_CLEAR', true)
      commit('SET_BUSY', false) // interupt loading
      commit('RESET_PAGINATOR')
      dispatch('fetchRecords')
    }
  },
  addRecord: ({ commit }, obj) => {
    commit('ADD_UPLOADED', obj)
    commit('ADD_RECORD', obj)
  },
  saveRecord: ({ commit, dispatch }, obj) => {
    axios.put('edit/' + obj.id, obj).then(response => {
      const obj = response.data.rec
      commit('UPDATE_RECORD', obj)
      commit('DELETE_UPLOADED', obj)
      commit('UPDATE_VALUES', obj)
      dispatch('_fetchLast')
    })
  },
  deleteRecord: ({ commit, dispatch }, obj) => {
    axios
      .delete('delete/' + obj.id, { parms: { foo: 'bar' } })
      .then(response => {
        if (response.data) {
          EventBus.$emit('snackbar', 'Successfully deleted ' + obj.headline)
          commit('DELETE_RECORD', obj)
          commit('DELETE_UPLOADED', obj)
          dispatch('_fetchLast')
        } else {
          EventBus.$emit('snackbar', 'Deleting failed ' + obj.headline)
        }
      })
  },
  fetchTotal: ({ commit }) => {
    axios.get('counter/total').then(response => {
      commit('SET_TOTAL', response.data)
    })
  },
  _fetchLast: debounce(({ dispatch }) => {
    dispatch('fetchLast')
  }, 200),
  fetchLast: ({ commit }) => {
    axios.get('counter/last').then(response => {
      commit('SET_LAST', response.data)
    })
  },
  fetchValues: ({ commit }) => {
    axios.get('counter/values').then(response => {
      commit('SET_VALUES', response.data)
    })
  },
  fetchRecords: ({ commit, state }) => {
    if (state.busy) return
    if (Object.keys(state.find).length) {
      const params = Object.assign({}, state.find, { per_page: LIMIT })
      if (state.next) params._page = state.next
      const url = 'search?' + querystring.stringify(params)

      commit('SET_ERROR', '')
      commit('SET_BUSY', true)
      axios
        .get(url)
        .then(response => {
          if (state.clear) {
            commit('RESET_RECORDS')
            commit('SET_CLEAR', false)
          }
          commit('UPDATE_RECORDS', response.data)
          if (response.error) commit('SET_ERROR', response.error)
          commit('SET_BUSY', false)
        })
        .catch(err => {
          commit('SET_ERROR', err)
          commit('SET_BUSY', false)
        })
    }
  },
  updateValuesEmail: ({ commit }, user) => {
    commit('UPDATE_VALUES_EMAIL', user)
  }
}

const mutations = {
  // [RESET]: state => ({ ...initialState }),
  SAVE_FIND_FORM (state, payload) {
    state.find = Object.assign({}, payload)
  },
  ADD_RECORD (state, obj) {
    const dates = state.objects.map(item => item.date)
    const idx = dates.findIndex(date => date < obj.date)
    state.objects.splice(idx, 0, obj)
    state.count++
    state.total++
  },
  ADD_UPLOADED (state, data) {
    state.uploaded = [...state.uploaded, data]
  },
  UPDATE_RECORDS (state, data) {
    if (state.pages[0] === 'FP' && data._page === 'FP') return
    state.objects = [...state.objects, ...data.objects]
    state.pages = [...state.pages, data._page]
    state.next = data._next
    state.count = state.objects.length
  },
  UPDATE_RECORD (state, obj) {
    if (state.objects && state.objects.length) {
      const idx = state.objects.findIndex(item => item.id === obj.id)
      state.objects.splice(idx, 1, obj)
    }
  },
  RESET_RECORDS (state) {
    state.objects.length = 0
  },
  RESET_PAGINATOR (state) {
    state.pages.length = 0
    state.next = null
  },
  DELETE_RECORD (state, obj) {
    const idx = state.objects.findIndex(item => item.id === obj.id)
    if (idx > -1) state.objects.splice(idx, 1)
    state.count--
    state.total--
  },
  DELETE_UPLOADED (state, obj) {
    const idx = state.uploaded.findIndex(item => item.id === obj.id)
    if (idx > -1) state.uploaded.splice(idx, 1)
  },
  UPDATE_VALUES (state, obj) {
    state.values.year = [...new Set([...state.values.year, 1 * obj.year])]
    state.values.tags = [...new Set([...state.values.tags, ...obj.tags])]
    if (obj.model) {
      state.values.model = [...new Set([...state.values.model, obj.model])]
    }
  },
  UPDATE_VALUES_EMAIL (state, user) {
    state.values.email = [...new Set([...state.values.email, user.email])]
  },
  SET_TOTAL (state, data) {
    state.total = data
  },
  SET_LAST (state, data) {
    state.last = data
  },
  SET_VALUES (state, data) {
    state.values = data
  },
  SET_CLEAR (state, val) {
    state.clear = val
  },
  SET_BUSY (state, val) {
    state.busy = val
  },
  SET_ERROR (state, val) {
    state.error = val
  }
}

export default {
  namespaced: true,
  state: initialState,
  mutations,
  actions
}
