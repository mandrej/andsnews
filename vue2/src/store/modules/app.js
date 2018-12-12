/* eslint no-console: ["error", { allow: ["warn", "error"] }] */
// export const RESET = 'RESET';
import Vue from 'vue'

const axios = Vue.axios
const LIMIT = 24

const initialState = {
  find: {},
  filter: {},
  uploaded: [],

  menu: [],
  objects: [],
  pages: [],
  next: null,
  error: '',
  values: {},

  total: null, // menu
  count: null,

  busy: false,
  clear: false
}
const actions = {
  // reset: ({ commit }) => commit(RESET),
  saveFindForm: ({ commit }, payload) => commit('SAVE_FIND_FORM', payload),
  changeFilter: ({ commit }, payload) => {
    commit('CHANGE_FILTER', payload)
    if (payload.field) {
      commit('SET_CLEAR', true)
      commit('SET_BUSY', false) // interupt loading
      commit('RESET_PAGINATOR')
    }
  },
  addRecord: ({ commit }, obj) => {
    commit('ADD_UPLOADED', obj)
    commit('ADD_RECORD', obj)
  },
  saveRecord: ({ commit, dispatch }, obj) => {
    axios.put('edit/' + obj.safekey, obj)
      .then(response => {
        const obj = response.data.rec
        commit('UPDATE_RECORD', obj)
        commit('DELETE_UPLOADED', obj)
        commit('UPDATE_VALUES', obj)
        dispatch('fetchMenu')
      })
  },
  deleteRecord: ({ commit, dispatch }, obj) => {
    axios.delete('delete/' + obj.safekey, { parms: { foo: 'bar' } }) // no response
    commit('DELETE_RECORD', obj)
    commit('DELETE_UPLOADED', obj)
    dispatch('fetchMenu')
  },
  fetchMenu: ({ commit }) => {
    axios.get('counter/filters')
      .then(response => {
        commit('UPDATE_MENU', response.data)
      })
  },
  fetchRecords: ({ commit, state }) => {
    if (state.busy) return
    const filter = { ...state.filter }

    if (filter && filter.field === 'search') {
      const url = [filter.field, filter.value].join('/')
      const params = { per_page: LIMIT }
      if (state.next) params._page = state.next

      commit('SET_ERROR', '')
      commit('SET_BUSY', true)
      axios.get(url, { params: params })
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
  fetchValues: ({ commit }) => {
    axios.get('counter/values')
      .then(response => {
        commit('SET_VALUES', response.data)
      })
  }
}
const mutations = {
  // [RESET]: state => ({ ...initialState }), // eslint-disable-line no-unused-vars
  SAVE_FIND_FORM (state, payload) {
    state.find = Object.assign(state.find, payload)
  },
  CHANGE_FILTER (state, payload) {
    state.filter = Object.assign({}, payload)
  },
  UPDATE_MENU (state, data) {
    state.total = data.count
    state.menu = [...data.filters]
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
    const idx = state.objects.findIndex(item => item.safekey === obj.safekey)
    state.objects.splice(idx, 1, obj)
  },
  RESET_RECORDS (state) {
    state.objects.length = 0
  },
  RESET_PAGINATOR (state) {
    state.pages.length = 0
    state.next = null
  },
  DELETE_RECORD (state, obj) {
    const idx = state.objects.findIndex(item => item.safekey === obj.safekey)
    if (idx > -1) state.objects.splice(idx, 1)
    state.count--
    state.total--
  },
  DELETE_UPLOADED (state, obj) {
    const idx = state.uploaded.findIndex(item => item.safekey === obj.safekey)
    if (idx > -1) state.uploaded.splice(idx, 1)
  },
  UPDATE_VALUES (state, obj) {
    state.values.year = [...new Set([...state.values.year, 1 * obj.year])]
    state.values.tags = [...new Set([...state.values.tags, ...obj.tags])]
    state.values.color = [...new Set([...state.values.color, obj.color])]
    if (obj.model) state.values.model = [...new Set([...state.values.model, obj.model])]
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
