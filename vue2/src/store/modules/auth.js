/* eslint no-console: ["error", { allow: ["warn", "error"] }] */
import Vue from 'vue'
import '@/helpers/fire' // initialized firebase instance
import firebase from 'firebase/app'
import 'firebase/auth'
import 'firebase/messaging'
import router from '@/router'
import CONFIG from '@/helpers/config'

const axios = Vue.axios
const messaging = firebase.messaging()
const provider = new firebase.auth.GoogleAuthProvider()
provider.addScope('profile')
provider.addScope('email')

function pushMessage (token, msg) {
  axios
    .post('message', { token: token, text: msg })
    .then()
    .catch(() => console.error('push message failed'))
}

const initialState = {
  user: {},
  fcm_token: null
}
const actions = {
  signIn: ({ commit, dispatch, state }) => {
    if (state.user && state.user.uid) {
      firebase.auth().signOut()
        .then(() => {
          commit('SAVE_USER', {})
          const routeName = router.currentRoute.name
          if (routeName === 'add' || routeName === 'admin') {
            router.replace({ name: 'home' })
          }
        })
    } else {
      firebase.auth().signInWithPopup(provider)
        .then(response => {
          const payload = {
            name: response.user.displayName,
            email: response.user.email,
            uid: response.user.uid,
            photo: response.user.photoURL,
            isAuthorized: true,
            isAdmin: CONFIG.admins.indexOf(response.user.uid) !== -1
          }
          commit('SAVE_USER', payload)
          dispatch('updateUser', payload)
          dispatch('fetchToken')
        }).catch(error => {
          console.error(error.message)
        })
    }
  },
  updateUser: ({ dispatch }, user) => {
    axios
      .post('user', { user: user })
      .then(response => {
        if (response.data.success) {
          dispatch('app/updateValuesEmail', user, { root: true })
        }
      })
      .catch(() => console.error('update user failed'))
  },
  fetchToken: ({ commit, state, dispatch }) => {
    if (state.user && state.user.uid) {
      Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
          return messaging
            .getToken()
            .then(token => {
              if (token) {
                commit('SET_TOKEN', token)
                dispatch('addRegistration')
              }
            })
            .catch(err => console.error(err))
        } else {
          console.error('Unable to get permission')
        }
      })
    }
  },
  addRegistration: ({ state }) => {
    axios.put('user/register', { uid: state.user.uid, token: state.fcm_token }).then().catch(err => console.error(err))
  },
  sendNotifications: ({ state }, msg) => {
    axios.get('registrations').then(response => {
      response.data.forEach(token => {
        if (token === state.fcm_token) {
          pushMessage(token, msg + ' sent successfully')
        } else {
          pushMessage(token, msg)
        }
      })
    })
  }
}
const mutations = {
  SAVE_USER (state, payload) {
    state.user = payload
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
