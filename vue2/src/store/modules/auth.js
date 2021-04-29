/* eslint no-console: ["error", { allow: ["warn", "error"] }] */
import Vue from 'vue'
import '@/helpers/fire' // initialized firebase instance
import pushMessage from '@/helpers/push'
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
            isAdmin: CONFIG.admins.indexOf(response.user.uid) !== -1,
            lastLogin: Date.now() // millis
          }
          commit('SAVE_USER', payload)
          dispatch('updateUser', payload)
          dispatch('getPermission')
        }).catch(err => {
          console.error(err.message)
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
  getPermission: ({ dispatch }) => {
    try {
      Notification.requestPermission().then(
        permission => dispatch('fetchToken', permission)
      )
    } catch (error) {
      // https://stackoverflow.com/questions/38114266
      // Safari doesn't return a promise for requestPermissions and it
      // throws a TypeError. It takes a callback as the first argument instead.
      if (error instanceof TypeError) {
        Notification.requestPermission(permission => {
          dispatch('fetchToken', permission)
        })
      } else {
        console.error(error.message)
      }
    }
  },
  fetchToken: ({ commit, state, dispatch }, permission) => {
    if (permission === 'granted') {
      return messaging
        .getToken({ vapidKey: CONFIG.firebase.vapidKey })
        .then(token => {
          if (token && token !== state.fcm_token) {
            commit('SET_TOKEN', token)
            if (state.user && state.user.uid) {
              dispatch('addRegistration')
            }
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
          pushMessage(token, msg + ' SENT')
        } else {
          pushMessage(token, msg)
        }
      })
    })
  }
}
const mutations = {
  SAVE_USER (state, payload) {
    state.user = { ...payload }
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
