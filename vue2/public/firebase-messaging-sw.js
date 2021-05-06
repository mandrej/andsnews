/* eslint-disable no-undef */
/* eslint-disable no-unused-vars */

// Give the service worker access to Firebase Messaging.
// Note that you can only use Firebase Messaging here, other Firebase libraries
// are not available in the service worker.
importScripts('https://www.gstatic.com/firebasejs/8.5.0/firebase-messaging.js')
importScripts('https://www.gstatic.com/firebasejs/8.5.0/firebase-app.js')

firebase.initializeApp({
  apiKey: 'AIzaSyBj5uKo0P_mir_ChQ_syx_kUQ_g7nkNy6M',
  authDomain: 'andsnews.firebaseapp.com',
  databaseURL: 'https://andsnews.firebaseio.com',
  projectId: 'andsnews',
  storageBucket: 'andsnews.appspot.com',
  messagingSenderId: '719127177629',
  appId: '1:719127177629:web:5e1335058fa70551186774'
})

// Retrieve an instance of Firebase Messaging so that it can handle background
// messages.
const messaging = firebase.messaging()
