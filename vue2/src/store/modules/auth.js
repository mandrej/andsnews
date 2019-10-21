/* eslint no-console: ["error", { allow: ["warn", "error"] }] */
import Vue from 'vue'
import { EventBus } from '@/helpers/event-bus'
import '@/helpers/fire' // initialized firebase instance
import firebase from '@firebase/app'
import '@firebase/auth'
import '@firebase/database'
import '@firebase/messaging'

const axios = Vue.axios
const messaging = firebase.messaging()
const provider = new firebase.auth.GoogleAuthProvider().addScope('email')
const admins = ['j8ezW5PBwMMnzrUvDA9ucYOOmrD3', 'vlRwHqVZNfOpr3FRqQZGqT2M2HA2']
// user.uid for  milan.andrejevic@gmail.com      mihailo.genije@gmail.com

function pushMessage (token, msg) {
  axios
    .post('message', { token: token, text: msg })
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
  signIn: ({ commit, dispatch, state }) => {
    if (state.user && state.user.uid) {
      firebase.auth()
        .signOut()
        .then(() => {
          commit('SAVE_USER', {})
        })
    } else {
      firebase.auth()
        .signInWithPopup(provider)
        .then(response => {
          const payload = {
            name: response.user.displayName,
            email: response.user.email,
            uid: response.user.uid,
            photo: response.user.photoURL,
            isAuthorized: true,
            isAdmin: admins.indexOf(response.user.uid) !== -1
          }
          commit('SAVE_USER', payload)
          dispatch('saveUser', payload)
        })
    }
  },
  saveUser: ({ dispatch }, user) => {
    firebase.database()
      .ref('users')
      .child(user.uid)
      .set({
        email: user.email,
        date: new Date().toISOString()
      })
    dispatch('app/updateValuesEmail', user, { root: true })
  },
  fetchToken: ({ commit, state, dispatch }) => {
    if (state.user && state.user.uid) {
      Notification
        .requestPermission()
        .then(() => {
          return messaging.getToken()
        })
        .then(token => {
          if (state.fcm_token !== token) {
            commit('SET_TOKEN', token)
            dispatch('addRegistration')
          }
        })
        .catch((err) => console.error(err))
    }
  },
  addRegistration: ({ state }) => {
    const ref = firebase.database().ref('registrations')
    ref.child(state.fcm_token).set({
      email: state.user.email,
      date: new Date().toISOString()
    })
    ref
      .orderByChild('email')
      .equalTo(state.user.email)
      .on('value', function (snapshot) {
        snapshot.forEach(function (data) {
          if (data.key !== state.fcm_token) {
            ref.child(data.key).remove()
          }
        })
      })
  },
  sendNotifications: ({ state }, msg) => {
    const ref = firebase.database().ref('registrations')
    ref.once('value', snapshot => {
      snapshot.forEach(node => {
        if (node.key !== state.fcm_token) {
          pushMessage(node.key, msg)
        }
      })
    })
  }
}
const mutations = {
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
