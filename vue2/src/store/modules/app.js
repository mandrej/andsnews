// export const RESET = 'RESET';
import Vue from 'vue'
/* eslint no-console: ["error", { allow: ["warn", "error"] }] */

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
  tags: [],
  models: [],

  total: null, // menu
  count: null,
  cloud: [], // info

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
  saveRecord: ({ commit }, obj) => {
    axios.put('photo/edit/' + obj.safekey, obj)
      .then(response => {
        const obj = response.data.rec
        commit('UPDATE_RECORD', obj)
        commit('DELETE_UPLOADED', obj)
        commit('UPDATE_TAGS_MODELS', obj)
      })
  },
  deleteRecord: ({ commit }, obj) => {
    commit('DELETE_RECORD', obj)
    commit('DELETE_UPLOADED', obj)
    axios.delete('delete/' + obj.safekey, { parms: { foo: 'bar' } }) // no response
  },
  fetchMenu: ({ commit, state }) => {
    if (state.busy) return
    commit('SET_BUSY', true)
    axios.get('filters')
      .then(response => {
        commit('UPDATE_MENU', response.data)
        commit('SET_BUSY', false)
      })
  },
  fetchRecords: ({ commit, state }) => {
    if (state.busy) return
    commit('SET_ERROR', '')
    commit('SET_BUSY', true)
    let url = 'start'
    const params = { per_page: LIMIT }
    const filter = { ...state.filter }
    if (state.next) params._page = state.next

    if (filter && filter.field) {
      if (filter.field === 'search') {
        url = ['search', filter.value].join('/')
      } else {
        url = ['photo', filter.field, filter.value].join('/')
      }
    }

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
  },
  fetchTags: ({ commit, state }) => {
    if (state.tags.length !== 0) return
    axios.get('suggest/Photo_tags')
      .then(response => {
        commit('UPDATE_TAGS', response.data)
      })
  },
  fetchModels: ({ commit, state }) => {
    if (state.models.length !== 0) return
    axios.get('suggest/Photo_model')
      .then(response => {
        commit('UPDATE_MODELS', response.data)
      })
  },
  fetchCloud: ({ commit }) => {
    axios.get('info')
      .then(response => {
        commit('SET_CLOUD', response.data)
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
    state.objects = [...state.objects, ...data.objects]
    state.pages = [...state.pages, data._page]
    state.next = data._next
    state.count = state.objects.length
  },
  UPDATE_RECORD (state, obj) {
    const idx = state.objects.findIndex(item => item.safekey === obj.safekey)
    state.objects.splice(idx, 1, obj)
  },
  UPDATE_TAGS_MODELS (state, obj) {
    state.tags = [...new Set([].concat(...state.tags, obj.tags))]
    if (obj.model) state.models = [...new Set([].concat(...state.models, [obj.model]))]
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
  UPDATE_TAGS (state, data) {
    state.tags = data
  },
  UPDATE_MODELS (state, data) {
    state.models = data
  },
  SET_CLOUD (state, payload) {
    state.cloud = payload
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
