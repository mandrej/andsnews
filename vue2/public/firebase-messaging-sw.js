/* eslint-disable no-undef */
/* eslint-disable no-unused-vars */

importScripts('https://www.gstatic.com/firebasejs/9.6.1/firebase-app-compat.js')
importScripts('https://www.gstatic.com/firebasejs/9.6.1/firebase-messaging-compat.js')

firebase.initializeApp({
  apiKey: 'AIzaSyBj5uKo0P_mir_ChQ_syx_kUQ_g7nkNy6M',
  authDomain: 'andsnews.firebaseapp.com',
  databaseURL: 'https://andsnews.firebaseio.com',
  projectId: 'andsnews',
  storageBucket: 'fullsized',
  messagingSenderId: '719127177629',
  appId: '1:719127177629:web:5e1335058fa70551186774'
})
const messaging = firebase.messaging()
