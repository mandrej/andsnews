import firebase from 'firebase'

const config = {
  apiKey: 'AIzaSyBj5uKo0P_mir_ChQ_syx_kUQ_g7nkNy6M',
  authDomain: 'andsnews.firebaseapp.com',
  databaseURL: 'https://andsnews.firebaseio.com',
  projectId: 'andsnews',
  storageBucket: 'andsnews.appspot.com',
  messagingSenderId: '719127177629'
}
const firebase_app = firebase.initializeApp(config)
export const FB = firebase_app

const messaging = firebase_app.messaging()
// messaging.usePublicVapidKey('BEMvPS8oRWveXcM6M_uBdQvDFZqvYKUOnUa22hVvMMlSMFr_04rI3G3BjJWW7EZKSqkM2mchPP3tReV4LY0Y45o')
export const MESSAGING = messaging
export const MESSAGING_SERVER_KEY = 'AAAAp29R6Z0:APA91bEsmfN6-ZywxP05Xpw-Ooto5FwTyXjgxRcqDllaTo6Kay3y8wnB-1QcwBt1-iQvoPt2p8wwp0JmKz4xWHST-pAQyrAivyTT-RFXasRYGmT09rP6oMuW95XHEi-HANZgzljuA-4i4Gh44den43zooddq5uSjBA'
