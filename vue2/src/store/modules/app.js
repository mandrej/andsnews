/* eslint no-console: ["error", { allow: ["warn", "error"] }] */
import Vue from 'vue'
import debounce from 'lodash/debounce'
import querystring from 'querystring'
import pushMessage from '../../helpers/push'
import CONFIG from '../../helpers/config'

const axios = Vue.axios

const state = {
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
  nickNames: (state) => {
    return state.values.email.map((email) => {
      return email.match(/[^@]+/)[0].split('.')[0]
    })
  },
  objectsByDate: (state) => {
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
  setUploadPercentage: ({ commit }, value) => {
    if (value === 100) {
      commit('changeUploadStatus', 2) // PROCESSING
    }
    commit('setUploadPercentage', value)
  },
  saveRecord: ({ commit, dispatch }, obj) => {
    if (obj.id) {
      axios.put('edit/' + obj.id, obj).then((response) => {
        const obj = response.data.rec
        commit('updateRecord', obj)
        commit('updateValues', obj)
      })
    } else {
      // publish
      axios.put('edit', obj).then((response) => {
        const obj = response.data.rec
        const diff = { verb: 'add', size: obj.size }
        commit('addRecord', obj)
        commit('deleteUploaded', obj)
        commit('updateValues', obj)
        dispatch('bucketInfo', diff)
      })
    }
  },
  deleteRecord: ({ commit, dispatch }, obj) => {
    if (obj.id) {
      axios
        .delete('delete/' + obj.id, { data: { foo: 'bar' } })
        .then((response) => {
          if (response.data) {
            const diff = { verb: 'del', size: obj.size }
            commit('setSnackbar', 'Successfully deleted ' + obj.filename)
            commit('deleteRecord', obj)
            dispatch('fetchStat')
            dispatch('bucketInfo', diff)
          } else {
            commit('setSnackbar', 'Deleting failed ' + obj.filename)
          }
        })
    } else {
      axios
        .delete('remove/' + obj.filename, { data: { foo: 'bar' } })
        .then((response) => {
          if (response.data) {
            commit('setSnackbar', 'Successfully deleted ' + obj.filename)
            commit('deleteUploaded', obj)
          } else {
            commit('setSnackbar', 'Deleting failed ' + obj.filename)
          }
        })
    }
  },
  changeFilter: ({ commit, dispatch }, payload) => {
    if (payload.reset) {
      commit('setClear', true)
      commit('setBusy', false) // interupt loading
      commit('resetPaginator')
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

    commit('setError', null)
    commit('setBusy', true)
    axios
      .get(url)
      .then((response) => {
        if (state.clear) {
          commit('resetObjects')
          commit('setClear', false)
        }
        if (response.data.objects && response.data.objects.length === 0) {
          commit('setError', 0)
        }
        if (response.error) commit('setError', response.error)
        commit('updateObjects', response.data)
        commit('setBusy', false)
      })
      .catch((err) => {
        commit('setSnackbar', err)
        commit('setBusy', false)
      })
  },
  fetchStat: ({ commit, dispatch, state }) => {
    axios.get('counters').then((response) => {
      commit('setValues', response.data)
      if (state.bucket.count === 0) {
        dispatch('bucketInfo', { verb: 'set' })
      }
    })
  },
  bucketInfo: debounce(({ dispatch }, param) => {
    dispatch('_bucketInfo', param)
  }, 2000),
  _bucketInfo: ({ commit, rootState }, param) => {
    /**
     * param: { verb: 'add|del|get', [size: int] }
     */
    if (param.verb === 'get') {
      axios.get(param.verb + '/bucket_info').then((response) => {
        commit('setBucket', response.data)
      })
    } else {
      axios.put(param.verb + '/bucket_info', param).then((response) => {
        if (param.verb === 'set') {
          pushMessage(rootState.auth.fcm_token, 'DONE')
        }
        commit('setBucket', response.data)
      })
    }
  }
}

const mutations = {
  addUploaded (state, data) {
    state.upload.list = [...state.upload.list, data]
  },
  deleteUploaded (state, obj) {
    const idx = state.upload.list.findIndex(
      (item) => item.filename === obj.filename
    )
    if (idx > -1) state.upload.list.splice(idx, 1)
  },
  addFailed (state, data) {
    state.upload.failed = [...state.upload.failed, data]
  },
  resetFailed (state) {
    state.upload.failed = []
  },
  changeUploadStatus (state, code) {
    state.upload.status = code
  },
  setUploadPercentage (state, value) {
    state.upload.value = value
  },
  addRecord (state, obj) {
    const dates = state.objects.map((item) => item.date)
    const idx = dates.findIndex((date) => date < obj.date)
    state.objects.splice(idx, 0, obj)
  },
  updateRecord (state, obj) {
    if (state.objects && state.objects.length) {
      const idx = state.objects.findIndex((item) => item.id === obj.id)
      state.objects.splice(idx, 1, obj)
    }
  },
  deleteRecord (state, obj) {
    const idx = state.objects.findIndex((item) => item.id === obj.id)
    if (idx > -1) state.objects.splice(idx, 1)
  },
  saveFindForm (state, payload) {
    state.find = { ...payload }
  },
  updateObjects (state, data) {
    if (state.pages[0] === 'FP' && data._page === 'FP') return
    state.objects = [...state.objects, ...data.objects]
    state.pages = [...state.pages, data._page]
    state.next = data._next
  },
  setClear (state, val) {
    state.clear = val
  },
  resetObjects (state) {
    state.objects.length = 0
  },
  resetPaginator (state) {
    state.pages.length = 0
    state.next = null
  },
  setBucket (state, obj) {
    state.bucket = { ...state.bucket, ...obj }
  },
  setValues (state, data) {
    CONFIG.photo_filter.forEach((field) => {
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
          ...Array.from(data[field], (c) => {
            return c.value
          })
        ]
      } else {
        state.values[field] = []
      }
    })
  },
  updateValues (state, obj) {
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
  updateValuesEmail (state, user) {
    state.values.email = [...new Set([...state.values.email, user.email])]
  },
  setBusy (state, val) {
    state.busy = val
  },
  setError (state, val) {
    state.error = val
  },
  setSnackbar (state, val) {
    state.snackbar = val
  },
  toggleTheme (state, val) {
    state.dark = val
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}
