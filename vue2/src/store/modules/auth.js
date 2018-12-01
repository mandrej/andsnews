/* eslint no-console: ["error", { allow: ["warn", "error"] }] */
// export const RESET = 'RESET';
import Vue from 'vue'
import { EventBus } from '@/helpers/event-bus'
import { FB } from '@/helpers/fire'
import 'firebase/app'
import 'firebase/database'

const axios = Vue.axios
const messaging = FB.messaging()

function pushMessage (token, msg) {
  axios.post('message', { token: token, text: msg })
    .then(response => {
      console.error(response)
    })
    .catch(() => console.error('push message failed'))
}

const initialState = {
  user: {},
  fcm_token: null
}
const actions = {
  // reset: ({ commit }) => commit(RESET),
  saveUser: ({ commit }, user) => {
    if (user && user.uid) {
      FB.database().ref('users').child(user.uid).set({
        email: user.email,
        date: (new Date()).toISOString()
      })
    }
    commit('SAVE_USER', user)
  },
  fetchToken: ({ commit, state, dispatch }) => {
    if (state.user && state.user.uid) {
      messaging.requestPermission()
        .then(() => {
          return messaging.getToken()
        })
        .then(token => {
          commit('SET_TOKEN', token)
          dispatch('addRegistration')
        })
        .catch(() => console.error('permission failed'))
    }
  },
  addRegistration: ({ state }) => {
    const ref = FB.database().ref('registrations')
    ref.child(state.fcm_token).set({
      email: state.user.email,
      date: (new Date()).toISOString()
    })
    ref.orderByChild('email').equalTo(state.user.email).on('value', function (snapshot) {
      snapshot.forEach(function (data) {
        if (data.key !== state.fcm_token) {
          ref.child(data.key).remove()
        }
      })
    })
  },
  sendNotifications: ({ state }, msg) => {
    const ref = FB.database().ref('registrations')
    ref.once('value', (snapshot) => {
      snapshot.forEach(node => {
        if (node.key !== state.fcm_token) {
          pushMessage(node.key, msg)
        }
      })
    })
  }
}
const mutations = {
  // [RESET]: state => ({ ...initialState }), // eslint-disable-line no-unused-vars
  SAVE_USER (state, payload) {
    state.user = payload
    EventBus.$emit('signin', state.user)
  },
  SET_TOKEN (state, val) {
    state.fcm_token = val
  }
}

export default {
  namespaced: true,
  state: initialState,
  mutations,
  actions
}
