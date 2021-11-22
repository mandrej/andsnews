/* eslint no-console: ["error", { allow: ["warn", "error"] }] */
import Vue from 'vue'
import debounce from 'lodash/debounce'
import querystring from 'querystring'
import pushMessage from '../../helpers/push'
import CONFIG from '../../helpers/config'
import { SET_SNACKBAR, TOGGLE_THEME, SAVE_FIND_FORM, ADD_RECORD, ADD_UPLOADED, ADD_FAILED, RESET_FAILED, SET_UPLOAD_PERCENTAGE,
CHANGE_UPLOAD_STATUS, UPDATE_OBJECTS, UPDATE_RECORD, RESET_OBJECTS, RESET_PAGINATOR, DELETE_RECORD, DELETE_UPLOADED, UPDATE_VALUES, 
UPDATE_VALUES_EMAIL, SET_VALUES, SET_CLEAR, SET_BUSY, SET_ERROR, SET_BUCKET } from '../mutation-types'

const axios = Vue.axios

const initialState = {
  find: {},

  upload: {
    list: [],
    failed: [],
    status: 0,
    value: 0
  },

  last: {
    count: 0,
    filename: null,
    date: new Date('1970-01-01').toISOString(),
    value: 1970
  },
  bucket: {
    size: 0,
    count: 0
  },
  values: {},

  objects: [],
  pages: [],
  next: null,
  error: null,

  busy: false,
  clear: false,
  dark: false,

  snackbar: null
}

const getters = {
  nickNames: state => {
    return state.values.email.map(email => {
      return email.match(/[^@]+/)[0].split('.')[0]
    })
  },
  objectsByDate: state => {
    return state.objects.reduce((groups, obj) => {
      const date = obj.date.slice(0, 10)
      if (!groups[date]) {
        groups[date] = []
      }
      groups[date].push(obj)
      return groups
    }, {})
  }
}

const actions = {
  addUploaded: ({ commit }, obj) => {
    commit(ADD_UPLOADED, obj)
  },
  addFailed: ({ commit }, obj) => {
    commit(ADD_FAILED, obj)
  },
  resetFailed: ({ commit }) => {
    commit(RESET_FAILED)
  },
  setUploadPercentage: ({ commit, dispatch }, value) => {
    if (value === 100) {
      dispatch('changeUploadStatus', 2) // PROCESSING
    }
    commit(SET_UPLOAD_PERCENTAGE, value)
  },
  changeUploadStatus: ({ commit }, status) => {
    commit(CHANGE_UPLOAD_STATUS, status)
  },
  saveRecord: ({ commit, dispatch }, obj) => {
    if (obj.id) {
      axios.put('edit/' + obj.id, obj).then(response => {
        const obj = response.data.rec
        commit(UPDATE_RECORD, obj)
        commit(UPDATE_VALUES, obj)
      })
    } else {
      // publish
      axios.put('edit', obj).then(response => {
        const obj = response.data.rec
        const diff = { verb: 'add', size: obj.size }
        commit(ADD_RECORD, obj)
        commit(DELETE_UPLOADED, obj)
        commit(UPDATE_VALUES, obj)
        dispatch('bucketInfo', diff)
      })
    }
  },
  deleteRecord: ({ commit, dispatch }, obj) => {
    if (obj.id) {
      axios
      .delete('delete/' + obj.id, { data: { foo: 'bar' } })
      .then(response => {
        if (response.data) {
          const diff = { verb: 'del', size: obj.size }
          commit(SET_SNACKBAR, 'Successfully deleted ' + obj.filename)
          commit(DELETE_RECORD, obj)
          dispatch('fetchStat')
          dispatch('bucketInfo', diff)
        } else {
          commit(SET_SNACKBAR, 'Deleting failed ' + obj.filename)
        }
      })
    } else {
      axios
      .delete('remove/' + obj.filename, { data: { foo: 'bar' } })
      .then(response => {
        if (response.data) {
          commit(SET_SNACKBAR, 'Successfully deleted ' + obj.filename)
          commit(DELETE_UPLOADED, obj)
        } else {
          commit(SET_SNACKBAR, 'Deleting failed ' + obj.filename)
        }
      })
    }
  },
  saveFindForm: ({ commit }, payload) => commit(SAVE_FIND_FORM, payload),
  changeFilter: ({ commit, dispatch }, payload) => {
    if (payload.reset) {
      commit(SET_CLEAR, true)
      commit(SET_BUSY, false) // interupt loading
      commit(RESET_PAGINATOR)
      dispatch('fetchRecords', payload.pid)
    }
  },
  fetchRecords: ({ commit, state }, pid) => {
    if (state.busy) return
    const params = Object.assign({}, state.find, {
      per_page: pid ? 2 * CONFIG.limit : CONFIG.limit
    })
    if (state.next) params._page = state.next
    const url = 'search?' + querystring.stringify(params)
     
    commit(SET_ERROR, null)
    commit(SET_BUSY, true)
    axios
    .get(url)
      .then(response => {
        if (state.clear) {
          commit(RESET_OBJECTS)
          commit(SET_CLEAR, false)
        }
        if (response.data.objects && response.data.objects.length === 0) {
          commit(SET_ERROR, 0)
        }
        if (response.error) commit(SET_ERROR, response.error)
        commit(UPDATE_OBJECTS, response.data)
        commit(SET_BUSY, false)
      })
      .catch(err => {
        commit(SET_SNACKBAR, err)
        commit(SET_BUSY, false)
      })
    },
  fetchStat: ({ commit, dispatch, state }) => {
    axios.get('counters').then(response => {
      commit(SET_VALUES, response.data)
      if (state.bucket.count === 0) {
        dispatch('bucketInfo', { verb: 'set' })
      }
    })
  },
  bucketInfo: debounce(({ dispatch }, param) => {
    dispatch('_bucketInfo', param)
  }, 1000),
  _bucketInfo: ({ commit, rootState }, param) => {
    /**
     * param: { verb: 'add|del|get', [size: int] }
     */
    if (param.verb === 'get') {
      axios.get(param.verb + '/bucket_info').then(response => {
        commit(SET_BUCKET, response.data)
      })
    } else {
      axios.put(param.verb + '/bucket_info', param).then(response => {
        if (param.verb === 'set') {
          pushMessage(rootState.auth.fcm_token, 'DONE')
        }
        commit(SET_BUCKET, response.data)
      })
    }
  },
  updateValuesEmail: ({ commit }, user) => {
    commit(UPDATE_VALUES_EMAIL, user)
  },
  toggleTheme: ({ commit }, val) => commit(TOGGLE_THEME, val),
  setSnackbar: ({ commit }, val) => commit(SET_SNACKBAR, val),
}
  
const mutations = {
  ADD_UPLOADED (state, data) {
    state.upload.list = [...state.upload.list, data]
  },
  DELETE_UPLOADED (state, obj) {
    const idx = state.upload.list.findIndex(
      item => item.filename === obj.filename
    )
    if (idx > -1) state.upload.list.splice(idx, 1)
  },
  ADD_FAILED (state, data) {
    state.upload.failed = [...state.upload.failed, data]
  },
  RESET_FAILED (state) {
    state.upload.failed = []
  },
  CHANGE_UPLOAD_STATUS (state, code) {
    state.upload.status = code
  },
  SET_UPLOAD_PERCENTAGE (state, value) {
    state.upload.value = value
  },
  ADD_RECORD (state, obj) {
    const dates = state.objects.map(item => item.date)
    const idx = dates.findIndex(date => date < obj.date)
    state.objects.splice(idx, 0, obj)
  },
  UPDATE_RECORD (state, obj) {
    if (state.objects && state.objects.length) {
      const idx = state.objects.findIndex(item => item.id === obj.id)
      state.objects.splice(idx, 1, obj)
    }
  },
  DELETE_RECORD (state, obj) {
    const idx = state.objects.findIndex(item => item.id === obj.id)
    if (idx > -1) state.objects.splice(idx, 1)
  },
  SAVE_FIND_FORM (state, payload) {
    state.find = { ...payload }
  },
  UPDATE_OBJECTS (state, data) {
    if (state.pages[0] === 'FP' && data._page === 'FP') return
    state.objects = [...state.objects, ...data.objects]
    state.pages = [...state.pages, data._page]
    state.next = data._next
  },
  SET_CLEAR (state, val) {
    state.clear = val
  },
  RESET_OBJECTS (state) {
    state.objects.length = 0
  },
  RESET_PAGINATOR (state) {
    state.pages.length = 0
    state.next = null
  },
  SET_BUCKET (state, obj) {
    state.bucket = { ...state.bucket, ...obj }
  },
  SET_VALUES (state, data) {
    CONFIG.photo_filter.forEach(field => {
      if (Object.prototype.hasOwnProperty.call(data, field)) {
        if (field === 'year') {
          const last = data.year[0]
          if (last) {
            state.last = {
              ...state.last,
              ...last
            }
          }
        }
        state.values[field] = [
          ...Array.from(data[field], c => {
            return c.value
          })
        ]
      } else {
        state.values[field] = []
      }
    })
  },
  UPDATE_VALUES (state, obj) {
    const lastFromState = new Date(state.last.date)
    const lastFromObject = new Date(obj.date)
    if (lastFromObject.getTime() > lastFromState.getTime()) {
      state.last = {
        ...state.last,
        ...{
          count: state.last.count + 1,
          filename: obj.filename,
          date: obj.date,
          value: lastFromObject.getFullYear()
        }
      }
    }
    state.values.year = [...new Set([...state.values.year, 1 * obj.year])]
    if (obj.tags) {
      state.values.tags = [...new Set([...state.values.tags, ...obj.tags])]
    }
    if (obj.model) {
      state.values.model = [...new Set([...state.values.model, obj.model])]
    }
    if (obj.lens) {
      state.values.lens = [...new Set([...state.values.lens, obj.lens])]
    }
    state.values.email = [...new Set([...state.values.email, obj.email])]
  },
  UPDATE_VALUES_EMAIL (state, user) {
    state.values.email = [...new Set([...state.values.email, user.email])]
  },
  SET_BUSY (state, val) {
    state.busy = val
  },
  SET_ERROR (state, val) {
    state.error = val
  },
  SET_SNACKBAR (state, val) {
    state.snackbar = val
  },
  TOGGLE_THEME (state, val) {
    state.dark = val
  },
}

export default {
  namespaced: true,
  state: initialState,
  mutations,
  actions,
  getters
}
