/* eslint no-console: ["error", { allow: ["warn", "error"] }] */
// export const RESET = 'RESET';
import Vue from 'vue'
import { EventBus } from '@/helpers/event-bus'
import debounce from 'lodash/debounce'
import querystring from 'querystring'
import CONFIG from '@/helpers/config'

const axios = Vue.axios

const initialState = {
  find: {},
  uploaded: [],

  last: {
    count: null,
    filename: null,
    date: new Date('1970-01-01').toISOString(),
    value: null
  },
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
  saveRecord: ({ commit }, obj) => {
    axios.put('edit/' + obj.id, obj).then(response => {
      const obj = response.data.rec
      commit('UPDATE_RECORD', obj)
      commit('DELETE_UPLOADED', obj)
      commit('UPDATE_VALUES', obj)
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
          dispatch('fetchStat')
        } else {
          EventBus.$emit('snackbar', 'Deleting failed ' + obj.headline)
        }
      })
  },
  fetchStat: debounce(({ dispatch }) => {
    dispatch('_fetchStat')
  }, 200),
  _fetchStat: ({ commit }) => {
    axios.get('counters').then(response => {
      commit('SET_COUNTERS', response.data)
    })
  },
  fetchRecords: ({ commit, state }) => {
    if (state.busy) return
    if (Object.keys(state.find).length) {
      const params = Object.assign({}, state.find, { per_page: CONFIG.limit })
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
    const last_stat_ts = new Date(state.last.date).getTime()
    const last_obj_ts = new Date(obj.date).getTime()
    if (last_obj_ts > last_stat_ts) {
      state.last = {
        count: null,
        filename: obj.filename,
        date: obj.date,
        value: null
      }
    }
    state.values.year = [...new Set([...state.values.year, 1 * obj.year])]
    if (obj.tags) {
      state.values.tags = [...new Set([...state.values.tags, ...obj.tags])]
    }
    if (obj.model) {
      state.values.model = [...new Set([...state.values.model, obj.model])]
    }
  },
  UPDATE_VALUES_EMAIL (state, user) {
    state.values.email = [...new Set([...state.values.email, user.email])]
  },
  SET_COUNTERS (state, data) {
    /**
     * state.last, state.total, state.values
     * from cloud.counters_stat
     */
    const _data = JSON.stringify(data)
    if (_data.indexOf('year') > 0) {
      const last = data.year[0]
      if (last) {
        state.last = last
      }
      if (_data.indexOf('count') > 0) {
        state.total = [...Array.from(data.year, c => {
          return c.count
        })].reduce((a, b) => a + b)
      }
    }

    state.values = {}
    CONFIG.photo_filter.forEach(field => {
      if (_data.indexOf(field) * _data.indexOf('value') > 0) {
        state.values[field] = [...Array.from(data[field], c => {
          return c.value
        })]
      } else {
        state.values[field] = []
      }
    })
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
