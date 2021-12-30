/* eslint no-console: ["error", { allow: ["warn", "error"] }] */
import Vue from 'vue'
import firebaseApp from '../../helpers/fire'
import { getAuth, signInWithPopup, GoogleAuthProvider } from 'firebase/auth'
import { getMessaging, getToken } from 'firebase/messaging'
import pushMessage from '../../helpers/push'
import router from '../../router'
import CONFIG from '../../helpers/config'
import { SAVE_USER, SET_TOKEN } from '../mutation-types'

const auth = getAuth(firebaseApp)
const messaging = getMessaging()
const axios = Vue.axios
const provider = new GoogleAuthProvider()
provider.addScope('profile')
provider.addScope('email')

const initialState = {
  user: {},
  fcm_token: null
}
const actions = {
  signIn: ({ commit, dispatch, state }) => {
    if (state.user && state.user.uid) {
      auth.signOut().then(() => {
        commit(SAVE_USER, {})
        const routeName = router.currentRoute.name
        if (routeName === 'add' || routeName === 'admin') {
          router.replace({ name: 'home' })
        }
      })
    } else {
      signInWithPopup(auth, provider)
        .then((response) => {
          const payload = {
            name: response.user.displayName,
            email: response.user.email,
            uid: response.user.uid,
            photo: response.user.photoURL,
            isAuthorized: true,
            isAdmin: CONFIG.admins.indexOf(response.user.uid) !== -1,
            lastLogin: Date.now() // millis
          }
          commit(SAVE_USER, payload)
          dispatch('updateUser', payload)
          dispatch('getPermission')
        })
        .catch((err) => {
          console.error(err.message)
        })
    }
  },
  updateUser: ({ dispatch }, user) => {
    axios
      .post('user', { user: user })
      .then((response) => {
        if (response.data.success) {
          dispatch('app/updateValuesEmail', user, { root: true })
        }
      })
      .catch(() => console.error('update user failed'))
  },
  getPermission: ({ dispatch }) => {
    try {
      Notification.requestPermission().then((permission) =>
        dispatch('fetchToken', permission)
      )
    } catch (error) {
      // https://developer.mozilla.org/en-US/docs/Web/API/Notifications_API/Using_the_Notifications_API
      Notification.requestPermission(function (permission) {
        dispatch('fetchToken', permission)
      })
    }
  },
  fetchToken: ({ commit, state, dispatch }, permission) => {
    if (permission === 'granted') {
      return getToken(messaging, { vapidKey: CONFIG.firebase.vapidKey })
        .then((token) => {
          if (token && token !== state.fcm_token) {
            commit(SET_TOKEN, token)
          }
          if (state.user && state.user.uid) {
            dispatch('addRegistration')
          }
        })
        .catch(function (err) {
          console.error('Unable to retrieve token ', err)
        })
    }
  },
  addRegistration: ({ state }) => {
    axios
      .put('user/register', { uid: state.user.uid, token: state.fcm_token })
      .then()
      .catch((err) => console.error(err))
  },
  // eslint-disable-next-line no-unused-vars
  sendNotifications: ({ state }, msg) => {
    axios.get('registrations').then(response => {
      pushMessage(response.data, msg)
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
