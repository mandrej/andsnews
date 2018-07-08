// export const RESET = 'RESET';
import Vue from 'vue'
import { FB } from '@/helpers/fire'
import 'firebase/app'
import 'firebase/database'
/* eslint-disable no-console */

const axios = Vue.axios
const messaging = FB.messaging()

function pushMessage (token) {
  axios.post('message', {token: token})
    .then(response => {
      console.log(response)
    })
    .catch(() => console.log('push message failed'))
}

const initialState = {
  user: {},
  find: {},
  filter: {},
  uploaded: [],
  fcm_token: null,

  objects: [],
  pages: [],
  page: null, // unused
  next: null,
  current: {},
  tags: [],
  models: [],

  total: null, // info
  count: null,
  counters: [], // info

  busy: false,
  clear: false
};
const getters = {
  // getTags: (state) => {
  //   return state.tags
  // },
}
const actions = {
  // reset: ({ commit }) => commit(RESET),
  saveUser: ({commit}, user) => {
    if (user && user.uid) {
      FB.database().ref('users').child(user.uid).set({
        email: user.email,
        date: (new Date()).toISOString()
      })
    }
    commit('SAVE_USER', user)
  },
  saveFindForm: ({commit}, payload) => commit('SAVE_FIND_FORM', payload),
  changeCurrent: ({commit}, payload) => commit('SET_CURRENT', payload),
  changeFilter: ({commit, dispatch}, payload) => {
    commit('CHANGE_FILTER', payload)
    commit('SET_CLEAR', true)
    dispatch('fetchRecords')
  },
  addRecord: ({commit}, obj) => {
    commit('ADD_UPLOADED', obj)
    commit('ADD_RECORD', obj)
  },
  saveRecord: ({commit}, obj) => {
    axios.put('photo/edit/' + obj.safekey, obj)
      .then(response => {
        const obj = response.data.rec
        commit('UPDATE_RECORD', obj)
        commit('SET_CURRENT', obj)
        commit('DELETE_UPLOADED', obj)
      })
  },
  deleteRecord: ({commit}, obj) => {
    commit('DELETE_RECORD', obj)
    commit('DELETE_UPLOADED', obj)
    axios.delete('delete/' + obj.safekey, {parms: {foo: 'bar'}})
      .then(response => {
        console.log(response.data)
      })
  },
  fetchRecords: ({commit, state}, next) => {
    let url = 'start'
    const params = {}
    const filter = {...state.filter}

    if (next) {
      params._page = next
    }
    if (filter && filter.field) {
      if (filter.field === 'search') {
        url = ['search', filter.value].join('/')
      } else {
        url = ['photo', filter.field, filter.value].join('/')
      }
    }

    commit('SET_BUSY', true)
    axios.get(url, {params: params})
      .then(response => {
        if (state.clear) {
          commit('RESET_RECORDS')
          commit('SET_CLEAR', false)
        }
        if (state.pages.indexOf(response.data._page) === -1) {
          commit('UPDATE_RECORDS', response.data)
        } else {
          console.log('duplicate ', response.data._page)
        }
        commit('SET_BUSY', false)
      })
      .catch(err => {
        commit('SET_BUSY', false)
        console.log(err)
      })
  },
  fetchTags: ({commit}) => {
    axios.get('suggest/Photo_tags')
      .then(response => {
        commit('UPDATE_TAGS', response.data)
      })
  },
  fetchModels: ({commit}) => {
    axios.get('suggest/Photo_model')
      .then(response => {
        commit('UPDATE_MODELS', response.data)
      })
  },
  fetchInfo: ({commit}) => {
    axios.get('info')
      .then(response => {
        commit('SET_INFO', response.data)
      })
  },
  fetchToken: ({commit, state, dispatch}) => {
    if (state.user && state.user.uid) {
      messaging.requestPermission()
        .then(() => {
          console.log('permission success')
          return messaging.getToken()
        })
        .then(token => {
          commit('SET_TOKEN', token)
          dispatch('subscribeToken')
        })
        .catch(() => console.log('permission failed'))
    }
  },
  subscribeToken: ({state}) => {
    const ref = FB.database().ref('registrations')
    ref.child(state.fcm_token).set({
      email: state.user.email,
      date: (new Date()).toISOString()
    })
  },
  sendNotifications: ({state}) => {
    const ref = FB.database().ref('registrations')
    ref.once('value', (shot) => {
      shot.forEach(child => {
        if (child.key !== state.fcm_token) {
          pushMessage(child.key)
        }
      })
    })
  }
};
const mutations = {
  // [RESET]: state => ({ ...initialState }), // eslint-disable-line no-unused-vars
  SAVE_USER (state, payload) {
    state.user = Object.assign(state.user, payload)
  },
  SET_CURRENT (state, payload) {
    state.current = Object.assign({}, payload)
  },
  SAVE_FIND_FORM (state, payload) {
    state.find = Object.assign(state.find, payload)
  },
  CHANGE_FILTER (state, payload) {
    state.filter = Object.assign({}, payload)
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
    state.page = data._page
    state.next = data._next
    state.count = state.objects.length
  },
  UPDATE_RECORD (state, obj) {
    const idx = state.objects.findIndex(item => item.safekey === obj.safekey)
    state.objects.splice(idx, 1, obj)
  },
  RESET_RECORDS (state) {
    state.objects.length = 0
    state.pages.length = 0
    state.page = null
    state.next = null
  },
  DELETE_RECORD (state, obj) {
    const idx = state.objects.findIndex(item => item.safekey === obj.safekey)
    state.objects.splice(idx, 1)
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
  SET_INFO (state, payload) {
    state.total = payload.photo.count
    state.counters = payload.photo.counters
  },
  SET_CLEAR (state, val) {
    state.clear = val
  },
  SET_BUSY (state, val) {
    state.busy = val
  },
  SET_TOKEN (state, val) {
    state.fcm_token = val
  }
};

export default {
  namespaced: true,
  state: initialState,
  getters,
  mutations,
  actions
};
